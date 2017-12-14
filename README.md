# README #

This README would normally document whatever steps are necessary to get your application up and running.

### What is this repository for? ###
This project is built for the Thesis Project Research in Hacettepe University
Version 1.0

* Quick summary
* Version 1.0

### How do I get set up? ###

* Summary of set up
* Configuration
* Dependencies
* Database configuration
* How to run tests
* Deployment instructions

### Contribution guidelines ###

* Writing tests
* Code review
* Other guidelines

## Development

On OSX:

    brew install crf++
    python setup.py install
    
  More information about
  CRFs can be found [here][crf_tut] and [here][nytimes].



### Who do I talk to? ###

* Repo owner or admin
* Other community or team contact

### DataSet Tagger WebSite
 * In order to generate precise dataset for evaluation we developed a website which repository is [here][recipePosMean] 
 * If you want to tag our dataset you can reach our website from [here][web] 



### Example Graph ###
Old code result:
![alt tag](https://github.com/ozgen/RecipePostagger/blob/master/results/result232.png)

After domain adaptation:

![alt tag](https://github.com/ozgen/RecipePostagger/blob/master/results/result232-2.png)


After optimization:

![alt tag](https://github.com/ozgen/RecipePostagger/blob/master/results/result232-3.png)


Other Result with Hidden Igredients:

![alt tag](https://github.com/ozgen/RecipePostagger/blob/master/results/result121.png)

After Domain Adaptaion:

![alt tag](https://github.com/ozgen/RecipePostagger/blob/master/results/result121-3.png)

latest results:
![alt tag](https://github.com/ozgen/RecipePostagger/blob/master/results/paper/beas-mashed-potato-salad.png)
![alt tag](https://github.com/ozgen/RecipePostagger/blob/master/results/paper/taco-soup-iv.png)


### DataSet Tagger WebSite 
The algorithm works on 28 tagged recipes which are from Kiddon. Its accuracy proportion is % 76,9713529622 


    






## Authors

* [Mehmet ÖZGEN][mo]
* [İbrahim ARDIÇ][ia]


[crf_tut]:  http://people.cs.umass.edu/~mccallum/papers/crf-tutorial.pdf
[nytimes]: https://github.com/NYTimes/ingredient-phrase-tagger
[recipePosMean]: https://github.com/ozgen/recipePostaggerMEAN
[web]: http://104.236.30.39:3000
[ia]: https://github.com/ardicib
[mo]: mailto:ozgenmehmett@gmail.com

