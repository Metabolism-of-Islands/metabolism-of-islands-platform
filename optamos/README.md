OPTamos readme
---------------

This readme provides specific details on how the OPTamos system is set up and integrated into the Metabolism of Islands platform.

## Logic

This is a regular Django project, using built-in options to manage Django views, urls, models, and templates. Review the readme for the [Metabolism of Island repository](https://github.com/Metabolism-of-Islands/metabolism-of-islands-platform) for a general overview of the platform. Within this repo, OPTamos is set up as a separate Django project, and most of the relevant files can be found in the dedicated folder within the project. Key files are discussed below.

`views.py:`

The most important part of the view is called project and it is where the logic is defined to load the interface where the user does the pairwise comparison, and where the values that are entered are saved. The user does two types of comparisons: comparing all the alternatives for a particular criterion, and comparing all the criteria against each other. Because the <input> and corresponding javascript is all quite similar, the same template file is being used. Results are also displayed using the same html file, as not to repeat HTML code.

In the views all `OptamosAlternative` are being loaded when the user is managing the comparison for a specific criteria. Pairs are automatically created by using the handy `itertools.combinations` function. This works in a very similar way when all the criteria are being evaluated, but now the `OptamosCriteria` records are being loaded.

The corresponding view section for the results groups together the code for the results page, the sensitivity analysis, and the file download - again as not to repeat too much code in the view (all of it builds off the data around the results).

In a development environment, mails will be logged to `./src/logs/mail.log/`.

Within the views there are quite a few comments that highlight what different sections do, and the best way to understand different parts is by going through this file.

`models.py:`

There are a handful of models, and they are all self-explanatory when looking at their definition and fieldnames.

Note that the `models.py` file is a shared file with the larger MoI project, so you will see many other models. However, all OPTamos models are prefaced by "Optamos" in the model name for easy recognition.

## CSS

The site uses TailwindCSS -- see the main repo for more info. 

## Additional details

- The background images that are loaded on each page are selected at random from a list of images defined in `views.py` (see OPTAMOS_BG). Each file comes from Pexels (which provides images that can be used without the need for credits, which is hard to do with background images). Files are cut to 300px height (maintaining 1920px width), sliced in general at the center of the image. The original filenames are maintained, making it possible to look up the original files at Pexels if need be.
- The meta-data for each project is simply to record internal details. Tags are shown on each project page (in the header, right top), but the description is not repeated in the front-end; it's simply visible when the user edits the project.
- Initially I calculated the Consistency Ratio not just for all the criteria that were ranked, but also for individual criteria based on the scores given to all alternatives. This was deemed unnecessary for the final user and is not displayed on the page, but the code remains present in the views -- removing it does not provide strong gains and just for internal debugging/viewing it might be useful.
- In the original OPTamos, the word 'option' was used for 'alternative'. This was initially migrated into this new version, but later changed to conform to norms in the field. While I did my best to remove all references, you might come across the word option here or there when talking about an alternative.
