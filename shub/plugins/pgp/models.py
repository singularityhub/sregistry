"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

Modified from: https://github.com/mugwort-rc/django-pgpdb
Commit: 763c2708c16bf58064f741ceb2e2ab752dea3663 (no LICENSE)

"""

import os
import base64
import uuid

from django.conf import settings

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import models
from django.db.models.signals import class_prepared, post_save, post_delete
from django.utils.timezone import make_aware, utc
from django.utils.translation import ugettext_lazy as _
from shub.apps.users.models import User

import pgpdump
from pgpdump.packet import (
    PublicKeyPacket,
    PublicSubkeyPacket,
    SignaturePacket,
    UserIDPacket,
)
from pgpdump.utils import crc24, PgpdumpException
from shub.plugins.pgp import utils


class PGPKeyModelManager(models.Manager):

    PGP_KEY_STORAGE = "pgpdb/{0}/{1}.pgp"

    def contribute_to_class(self, model, name):
        super(PGPKeyModelManager, self).contribute_to_class(model, name)
        class_prepared.connect(self.class_prepared, sender=self.model)

    def class_prepared(self, sender, **kwargs):
        post_save.connect(self.post_save, sender=self.model)
        post_delete.connect(self.post_delete, sender=self.model)

    def post_save(self, sender, instance, created, **kwargs):
        if created:
            data = instance.file.read()
            pgp = None
            try:
                pgp = pgpdump.AsciiData(data)
            except PgpdumpException:
                pgp = pgpdump.BinaryData(data)
            instance.file.save(instance.file.name, ContentFile(pgp.data))
            crc = crc24(pgp.data)
            crc_bin = crc.to_bytes(3, "big")
            instance.crc24 = base64.b64encode(crc_bin).decode("utf-8")
            instance.save()

            # parse packets
            index = 0
            last_pubkey = None
            last_userid = None
            for packet in pgp.packets():
                index += 1
                if (
                    not isinstance(packet, PublicKeyPacket)
                    and not isinstance(packet, UserIDPacket)
                    and not isinstance(packet, SignaturePacket)
                ):
                    continue
                if isinstance(packet, PublicKeyPacket):
                    is_sub = isinstance(packet, PublicSubkeyPacket)
                    creation_time = make_aware(packet.creation_time, utc)
                    expir = None
                    if packet.expiration_time is not None:
                        expir = make_aware(packet.expiration_time, utc)
                    algo = packet.raw_pub_algorithm
                    bits = 0
                    if algo in (1, 2, 3):
                        bits = len(bin(packet.modulus)[2:])
                    elif algo == 17:
                        bits = len(bin(packet.prime)[2:])
                    elif algo in (16, 20):
                        bits = len(bin(packet.prime)[2:])
                    fingerprint = packet.fingerprint.lower().decode("utf-8")
                    keyid = packet.key_id.lower().decode("utf-8")
                    last_pubkey = PGPPublicKeyModel.objects.create(
                        index=index,
                        key=instance,
                        is_sub=is_sub,
                        creation_time=creation_time,
                        expiration_time=expir,
                        algorithm=algo,
                        bits=bits,
                        fingerprint=fingerprint,
                        keyid=keyid,
                    )
                elif isinstance(packet, UserIDPacket):
                    userid = packet.data.decode("utf-8")
                    last_userid = PGPUserIDModel.objects.create(
                        index=index, key=instance, userid=userid
                    )
                elif isinstance(packet, SignaturePacket) and last_userid:
                    creation_time = make_aware(packet.creation_time, utc)
                    expir = None
                    if packet.expiration_time is not None:
                        expir = make_aware(packet.expiration_time, utc)
                    keyid = packet.key_id.lower().decode("utf-8")
                    PGPSignatureModel.objects.create(
                        index=index,
                        key=instance,
                        pkey=last_pubkey,
                        userid=last_userid,
                        type=packet.raw_sig_type,
                        pka=packet.raw_pub_algorithm,
                        hash=packet.raw_hash_algorithm,
                        creation_time=creation_time,
                        expiration_time=expir,
                        keyid=keyid,
                    )

    def post_delete(self, sender, instance, **kwargs):
        """\sa: self.post_save()"""
        instance.file.delete(False)

    def save_to_storage(self, user, data):
        uid = str(uuid.uuid4())
        path = PGPKeyModelManager.PGP_KEY_STORAGE.format(uid[:2], uid[2:])
        fp = default_storage.save(path, ContentFile(data))
        return self.create(uid=uid, user=user, file=fp)


def _pgp_key_model_upload_to(instance, filename):
    uid = instance.uid
    path = PGPKeyModelManager.PGP_KEY_STORAGE.format(uid[:2], uid[2:])
    return os.path.join(settings.MEDIA_ROOT, path)


class PGPKeyModel(models.Model):
    uid = models.UUIDField()

    # When a user is deleted, we still want to keep keys
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.DO_NOTHING)
    file = models.FileField(upload_to=_pgp_key_model_upload_to, storage=default_storage)
    crc24 = models.CharField(max_length=4)  # =([A-Za-z0-9+/]{4})
    is_revoked = models.BooleanField(default=False)

    objects = PGPKeyModelManager()

    def first(self):
        return {
            "public_key": self.public_keys.order_by("id").first(),
            "userid": self.userids.order_by("id").first(),
        }

    def packets(self):
        result = []
        result += [x for x in self.public_keys.all()]
        result += [x for x in self.userids.all()]
        result += [x for x in self.signatures.all()]
        return sorted(result, key=lambda x: x.index)

    def ascii_armor(self):
        data = self.read()
        return utils.encode_ascii_armor(data, self.crc24)

    def read(self):
        return self.file.read()


class PGPPacketModel(models.Model):
    index = models.IntegerField()

    class Meta:
        abstract = True

    def is_public_key(self):
        return False

    def is_userid(self):
        return False

    def is_signature(self):
        return False


# Tag 6, Tag14
class PGPPublicKeyModel(PGPPacketModel):

    UNKNOWN = 0
    RSA_ENC_SIGN = 1
    RSA_ENC = 2
    RSA_SIGN = 3
    ELGAMAL_ENC = 16
    DSA = 17
    ECDH = 18
    ECDSA = 19
    ELGAMAL_ENC_SIGN = 20
    DH = 21

    PKA_MAP = {
        UNKNOWN: _("Unknown"),
        RSA_ENC_SIGN: _("RSA (Encrypt or Sign)"),
        RSA_ENC: _("RSA Encrypt-Only"),
        RSA_SIGN: _("RSA Sign-Only"),
        ELGAMAL_ENC: _("Elgamal (Encrypt-Only)"),
        DSA: _("DSA (Digital Signature Algorithm)"),
        ECDH: _("ECDH public key algorithm"),
        ECDSA: _("ECDSA public key algorithm"),
        ELGAMAL_ENC_SIGN: _("formerly Elgamal Encrypt or Sign"),
        DH: _("Diffie-Hellman"),
    }

    SIMPLE_PKA_MAP = {
        UNKNOWN: _("Unknown"),
        RSA_ENC_SIGN: _("RSA"),
        RSA_ENC: _("RSA"),
        RSA_SIGN: _("RSA"),
        ELGAMAL_ENC: _("Elgamal"),
        DSA: _("DSA"),
        ECDH: _("ECDH"),
        ECDSA: _("ECDSA"),
        ELGAMAL_ENC_SIGN: _("Elgamal"),
        DH: _("DH"),
    }

    key = models.ForeignKey(
        "PGPKeyModel", related_name="public_keys", on_delete=models.CASCADE
    )
    is_sub = models.BooleanField(default=False)
    creation_time = models.DateTimeField()
    expiration_time = models.DateTimeField(null=True)
    algorithm = models.IntegerField(
        default=0,
        choices=(
            (UNKNOWN, PKA_MAP[UNKNOWN]),
            (RSA_ENC_SIGN, PKA_MAP[RSA_ENC_SIGN]),
            (RSA_ENC, PKA_MAP[RSA_ENC]),
            (RSA_SIGN, PKA_MAP[RSA_SIGN]),
            (ELGAMAL_ENC, PKA_MAP[ELGAMAL_ENC]),
            (DSA, PKA_MAP[DSA]),
            (ECDH, PKA_MAP[ECDH]),
            (ECDSA, PKA_MAP[ECDSA]),
            (ELGAMAL_ENC_SIGN, PKA_MAP[ELGAMAL_ENC_SIGN]),
            (DH, PKA_MAP[DH]),
        ),
    )
    bits = models.IntegerField()
    fingerprint = models.TextField()
    keyid = models.CharField(max_length=255)

    def algorithm_str(self):
        return str(self.PKA_MAP[self.algorithm])

    def simple_algorithm_str(self):
        return str(self.SIMPLE_PKA_MAP[self.algorithm])

    def is_public_key(self):
        return True


# Tag 13
class PGPUserIDModel(PGPPacketModel):
    key = models.ForeignKey(
        "PGPKeyModel", related_name="userids", on_delete=models.CASCADE
    )
    userid = models.TextField()

    def is_userid(self):
        return True


# Tag 2
class PGPSignatureModel(PGPPacketModel):

    SIG_UNKNOWN = -1
    BINARY = 0x00
    TEXT = 0x01
    STANDALONE = 0x02
    KEY_GENERAL = 0x10
    KEY_PERSONAL = 0x11
    KEY_CASUAL = 0x12
    KEY_POSITIVE = 0x13
    BINDING = 0x18
    DIRECT = 0x1F
    KEY_REVOKE = 0x20
    SUBKEY_REVOKE = 0x28
    ID_REVOKE = 0x30
    TIMESTAMP = 0x40

    SIG_MAP = {
        SIG_UNKNOWN: _("Unknown"),
        BINARY: _("Binary"),
        TEXT: _("Text"),
        STANDALONE: _("Standalone"),
        KEY_GENERAL: _("Key General"),
        KEY_PERSONAL: _("Key Personal"),
        KEY_CASUAL: _("Key Casual"),
        KEY_POSITIVE: _("Key Personal"),
        BINDING: _("Binding"),
        DIRECT: _("Direct"),
        KEY_REVOKE: _("Key Revoke"),
        SUBKEY_REVOKE: _("SubKey Revoke"),
        ID_REVOKE: _("ID Revoke"),
        TIMESTAMP: _("Timestamp"),
    }

    UNKNOWN = PGPPublicKeyModel.UNKNOWN
    RSA_ENC_SIGN = PGPPublicKeyModel.RSA_ENC_SIGN
    RSA_ENC = PGPPublicKeyModel.RSA_ENC
    RSA_SIGN = PGPPublicKeyModel.RSA_SIGN
    ELGAMAL_ENC = PGPPublicKeyModel.ELGAMAL_ENC
    DSA = PGPPublicKeyModel.DSA
    ECDH = PGPPublicKeyModel.ECDH
    ECDSA = PGPPublicKeyModel.ECDSA
    ELGAMAL_ENC_SIGN = PGPPublicKeyModel.ELGAMAL_ENC_SIGN
    DH = PGPPublicKeyModel.DH

    PKA_MAP = PGPPublicKeyModel.PKA_MAP
    SIMPLE_PKA_MAP = PGPPublicKeyModel.SIMPLE_PKA_MAP

    MD5 = 1
    SHA1 = 2
    RIPEMD160 = 3
    RESERVED4 = 4
    RESERVED5 = 5
    RESERVED6 = 6
    RESERVED7 = 7
    SHA256 = 8
    SHA384 = 9
    SHA512 = 10
    SHA224 = 11

    HASH_MAP = {
        UNKNOWN: PKA_MAP[UNKNOWN],
        MD5: _("MD5"),
        SHA1: _("SHA1"),
        RIPEMD160: _("RIPEMD160"),
        RESERVED4: _("Reserved (4)"),
        RESERVED5: _("Reserved (5)"),
        RESERVED6: _("Reserved (6)"),
        RESERVED7: _("Reserved (7)"),
        SHA256: _("SHA256"),
        SHA384: _("SHA384"),
        SHA512: _("SHA512"),
        SHA224: _("SHA224"),
    }

    key = models.ForeignKey(
        "PGPKeyModel", related_name="signatures", on_delete=models.CASCADE
    )
    pkey = models.ForeignKey(
        "PGPPublicKeyModel", related_name="signatures", on_delete=models.CASCADE
    )
    userid = models.ForeignKey(
        "PGPUserIDModel", related_name="signatures", on_delete=models.CASCADE
    )
    type = models.IntegerField(
        default=-1,
        choices=(
            (SIG_UNKNOWN, SIG_MAP[SIG_UNKNOWN]),
            (BINARY, SIG_MAP[BINARY]),
            (TEXT, SIG_MAP[TEXT]),
            (STANDALONE, SIG_MAP[STANDALONE]),
            (KEY_GENERAL, SIG_MAP[KEY_GENERAL]),
            (KEY_PERSONAL, SIG_MAP[KEY_PERSONAL]),
            (KEY_CASUAL, SIG_MAP[KEY_CASUAL]),
            (KEY_POSITIVE, SIG_MAP[KEY_POSITIVE]),
            (BINDING, SIG_MAP[BINDING]),
            (DIRECT, SIG_MAP[DIRECT]),
            (KEY_REVOKE, SIG_MAP[KEY_REVOKE]),
            (SUBKEY_REVOKE, SIG_MAP[SUBKEY_REVOKE]),
            (ID_REVOKE, SIG_MAP[ID_REVOKE]),
            (TIMESTAMP, SIG_MAP[TIMESTAMP]),
        ),
    )
    pka = models.IntegerField(
        default=0,
        choices=(
            (UNKNOWN, PKA_MAP[UNKNOWN]),
            (RSA_ENC_SIGN, PKA_MAP[RSA_ENC_SIGN]),
            (RSA_ENC, PKA_MAP[RSA_ENC]),
            (RSA_SIGN, PKA_MAP[RSA_SIGN]),
            (ELGAMAL_ENC, PKA_MAP[ELGAMAL_ENC]),
            (DSA, PKA_MAP[DSA]),
            (ECDH, PKA_MAP[ECDH]),
            (ECDSA, PKA_MAP[ECDSA]),
            (ELGAMAL_ENC_SIGN, PKA_MAP[ELGAMAL_ENC_SIGN]),
            (DH, PKA_MAP[DH]),
        ),
    )
    hash = models.IntegerField(
        default=0,
        choices=(
            (UNKNOWN, HASH_MAP[UNKNOWN]),
            (MD5, HASH_MAP[MD5]),
            (SHA1, HASH_MAP[SHA1]),
            (RIPEMD160, HASH_MAP[RIPEMD160]),
            (RESERVED4, HASH_MAP[RESERVED4]),
            (RESERVED5, HASH_MAP[RESERVED5]),
            (RESERVED6, HASH_MAP[RESERVED6]),
            (RESERVED7, HASH_MAP[RESERVED7]),
            (SHA256, HASH_MAP[SHA256]),
            (SHA384, HASH_MAP[SHA384]),
            (SHA512, HASH_MAP[SHA512]),
            (SHA224, HASH_MAP[SHA224]),
        ),
    )
    creation_time = models.DateTimeField()
    expiration_time = models.DateTimeField(null=True)
    keyid = models.CharField(max_length=255)

    def type_str(self):
        return str(self.SIG_MAP[self.type])

    def pka_str(self):
        return str(self.PKA_MAP[self.pka])

    def simple_pka_str(self):
        return str(self.SIMPLE_PKA_MAP[self.pka])

    def hash_str(self):
        return str(self.HASH_MAP[self.hash])

    def is_signature(self):
        return True
