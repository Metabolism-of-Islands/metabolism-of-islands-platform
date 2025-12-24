OPTamos documentation
---------------------

## CSS

OPTamos uses TailwindCSS (https://tailwindcss.com/)
A custom CSS using TailwindCSS is created, only including classes and other CSS statements that are relevant to the website. This custom css is created through nodejs, see the instructions here (https://tailwindcss.com/docs/installation/tailwind-cli). The required node packages are installed in the Docker container when it's built (see apt-get install .... nodejs npm). You might need to install the TailwindCSS package within your container:

$ ./openbash
(this will open bash within your container environment)
$ npm install tailwindcss @tailwindcss/cli

Once this is installed, you can run the following script:

(this is set up so you can run it from OUTSIDE your container and you don't have to open your container and run custom commands every time you want to refresh your css)

$ ./css_create

This will generate the required css in a file called optamos.css, which is already included in all optamos pages.
