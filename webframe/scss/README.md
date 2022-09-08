Compile SCSS

The package is develed under scss code. It can be customizes the style by scss engine. Execute the following code to compile:

docker run --rm -v $(pwd):$(pwd) -w $(pwd) jbergknoff/sass base-theme.scss > ../static/webframe/css/base-theme.css
