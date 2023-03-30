;(function () {

    'use strict';

    // iPad and iPod detection
    var isiPad = function(){
        return (navigator.platform.indexOf("iPad") != -1);
    };

    var isiPhone = function(){
        return (
            (navigator.platform.indexOf("iPhone") != -1) ||
            (navigator.platform.indexOf("iPod") != -1)
        );
    };

    var animateBox = function() {
        if ( $('.animate-box').length > 0 ) {
            $('.animate-box').waypoint( function( direction ) {

                if( direction === 'down' && !$(this.element).hasClass('animated') ) {

                    $(this.element).addClass('fadeIn animated');

                }
            } , { offset: '80%' } );
        }
    };


    var animateTeam = function() {
        if ( $('#fh5co-team').length > 0 ) {
            $('#fh5co-team .to-animate').each(function( k ) {

                var el = $(this);

                setTimeout ( function () {
                    console.log('yaya');
                    el.addClass('fadeInUp animated');
                },  k * 200, 'easeInOutExpo' );

            });
        }
    };
    var teamWayPoint = function() {
        if ( $('#fh5co-team').length > 0 ) {
            $('#fh5co-team').waypoint( function( direction ) {

                if( direction === 'down' && !$(this.element).hasClass('animated') ) {

                    setTimeout(animateTeam, 200);

                    $(this.element).addClass('animated');

                }
            } , { offset: '80%' } );
        }
    };

    $(function(){

        animateBox();
        teamWayPoint();

    });


}());
