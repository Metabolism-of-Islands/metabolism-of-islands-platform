OPTamos readme
---------------

This readme provides specific details on how the OPTamos system is set up and integrated into the Metabolism of Islands platform.

## CSS

OPTamos uses [TailwindCSS](https://tailwindcss.com/).

A custom CSS using TailwindCSS is created, only including classes and other CSS statements that are relevant to the website. This custom CSS is created through Node.js; see the instructions [here](https://tailwindcss.com/docs/installation/tailwind-cli). The required Node packages are installed in the Docker container when it's built (see `apt-get install .... nodejs npm`).

You might need to install the TailwindCSS package within your container:

```
$ ./openbash
```

(this will open bash within your container environment)

```
$ npm install tailwindcss @tailwindcss/cli
```

Once this is installed, you can run the following script:

(this is set up so you can run it from **OUTSIDE** your container and you don't have to open your container and run custom commands every time you want to refresh your CSS)

```
$ ./css_create
```

This will generate the required CSS in a file called `optamos.css`, which is already included in all OPTamos pages.

## Logic

This is a regular Django project, using built-in options to manage Django views, urls, models, and templates. 

`views.py:`

The most complex view is called project and it is where the logic is defined to load the interface where the user does the pairwise comparison, and where the values that are entered are saved. The user does two types of comparisons: comparing all the options for a particular criteria, and comparing all the criteria against the main goal. Because the <input> and corresponding javascript is all quite similar, the same template file is being used.

In the views all `OptamosOption` are being loaded when the user is managing the comparison for a specific criteria. Pairs are automatically created by using the handy `itertools.combinations` function. This works in a very similar way when all the criteria are being evaluated, but now the `OptamosCriteria` records are being loaded.

`models.py:`

There are a handful of models, and they are all self-explanatory when looking at their definition and fieldnames.

Note that the models.py file is a shared file with the larger MoI project, so you will see many other models. However, all OPTamos models are prefaced by "Optamos" in the model name for easy recognition.



