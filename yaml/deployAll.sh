find -iname *yaml | tr '\n' ',' | head --bytes -1 | xargs kubectl apply -f 
