# Projectweek : the manual

## Introduction

The document will describe everything about the projectweek that is not in one of the workshops. It's also the document that you'll start going through. We'll talk about how to make a game, come up with an idea for your game, where to find help.... 

You might have noticed that this document is light on the specifics on how to actually make a game (technical documentation). This is deliberate. We want to give you the absolute minimum to get you to have a minimal application where each team member can start working on different parts. We also refer to a sample pack, which is a collection of small, self contained examples of techniques that you can use in your own. And, of course, ChatGPT, pygame documentation, are all available. For the remaining questions you might have, talk to one of the lecturers or students. We've all done projectweek too :)

Why do it this way? Until know, all your materials have been linear paths to follow. Do A, check that it works, do B, etc... When you work in IT, that's absolutely *not* how it will be. You'll have to identify what knowledge you need and don't have, and spend as little time as possible finding and reading it. Don't worry though, if you do lose the plot (you don't know what to do next, or where to find information), just ask for help. 

Lastly, I mentioned it during the presentation, but I want to repeat: I'm really, really exited to see your game! Let's have a fun game jam euh I mean projectweek.


## Tutorial

### Setup

0. Form a group (get a group number on toledo), and make a group name
1. One student should go to the [classroom]
(https://classroom.github.com/assignment-invitations/6f5cc2057dcfa48a1943825395b03ba5) and accept the assignment. Find your name in the list and enters name of their group in this format: ## {GROUP_NUMBER) Team Name, (for example: 17 Lucky Seventeens, or 09 Dancing Queens)
2. Add the following file to the root of the project, commit, and push. [.gitignore](https://raw.githubusercontent.com/github/gitignore/master/Python.gitignore)
3. The rest of the team members should then click the link, find their name, then find the correct team.
4. Everyone should clone the empty repository to their local disk. "Local disk" is very important here, **DO NOT CLONE IT ONTO ONEDRIVE OR ANY OTHER CLOUD STORAGE**. The reason is that git does everything onedrive does (version control, available in the cloud), but especially, git and onedrive don't play nice together (long story short, because they do the same thing). It causes strange errors that give no indication as to what the cause is.

### Hello World

Before everyone start talking about what game to make, or starts coding, let's do it in a smart way.

1. Nobody can really start until there's a basic application that different things (like audio, keyboard input, gameplay) can hook into. Imagine it like an octopus: we need the body before we can attach the legs. We start by using 
    One person in your team (plus one pair programmer), ideally the fasted reader / coder should read and follow the following pages:
    * [Setting up](http://projectweek.leone.ucll.be/stories/setting-up/index.html) EXCEPT the project management part
    * [Hello pygame](http://projectweek.leone.ucll.be/stories/hello-pygame/index.html)
    * [Create window](http://projectweek.leone.ucll.be/stories/gui/create-window/index.html)
    * Commit and push to the repository

    While they wait, another person can (each bullet can be done by another person)
    * Go to [Setting up](http://projectweek.leone.ucll.be/stories/setting-up/index.html) and only do the project management part
    * Check out the other resources

    While they wait, everyone else has
    * run 'pip install pygame' in their terminal
    * And of course, start talking about what game you want to make!

    But let the first person work, you're all waiting on them. This should take an hour, tops (ask for help if you're stuck for more than 15 minutes, also outside of that). Once they're done
    * The person who follow it will commit and push their work
    * Everyone else will pull the code
    * Try and run the program, and make sure you have the same result
    * Make sure everyone has everything running correctly before advancing to the next step

2. Now we're starting in earnest. We can start adding functionality. That might seem weird, but most code you write won't be about your game specifically (the gameplay code). I recommend you split up, and do the following tasks (all independent bullets) in parallell (one, or two people (pair programming) per bullet). Don't forget to commit and push as often as you can.
    * read this document top to bottom (there's some good stuff beyond the tutorial you want to know0
    * learn about graphics programming by following [Drawing a circle](http://projectweek.leone.ucll.be/stories/gui/graphics/draw-circle/index.html), then [Naive animation](http://projectweek.leone.ucll.be/stories/gui/graphics/animation/naive-animation/index.html), and [Clearing the buffer]( http://projectweek.leone.ucll.be/stories/gui/graphics/animation/clearing-buffer/index.html). Afterwards you can follow the Graphics, Images, and Background sections in [the graph](http://projectweek.leone.ucll.be/graph.svg), or use one of the other online sources.
    * learn about gameplay programming (much more will come in the workshop) by following the box "Game" in [the graph](http://projectweek.leone.ucll.be/graph.svg)
    * learn about audio programming in the `Audio` section of  [the graph](http://projectweek.leone.ucll.be/graph.svg) (it might sound too early, but audio is very important for capturing the "feel" of a game. Don't forget to use headphones ;)
    
And that's.. not it. Now we can properly start. And by we, I mean you ;) Jokes aside, attend the workshops, talk to your teammates (and other teams, they'll have similar problems to you, and might have found the solutions), check online documentation. And, above all else, ask for help, and have fun!
    
## Deliverables

### Game

We want you to make a game, and we want you to spend all week on it (you can't be done early. If you don't know what to add, ask me).

The requirement are:

* It must be able to run on most machines (installing specific modules etc is ok)
* It's playable for at least one minute ('playable' is a fuzzy concept, but it's impossible to define what a game is. Ask me if in doubt)
* It follows the [Global Game Jam Code of Conduct](https://v3.globalgamejam.org/inclusiveness-policy-and-code-conduct). It's not a very clear document, but the first paragraph of "Appropriate behaviour" refers to your game as well. An easy rule of thumb is "If I'm not sure my game follows the rules", you should ask me if it does. A simpler one is "would I post this game on linkedin and keep it there during my career"

What we explicitly don't care about (you are allowed to, but we want to make it clear it's an option)

* Your game uses extra hardware such as a controller, webcam, microphone, heart rate monitor, etc
* Your game involves other software not in python, eg a database, or a c++ driver for... something. We do *not* recommend this, we do recommend you ask a lecturer when you want to do this, to see if there's another solution

### Attributions

You will probably use some assets (an asset is any piece of media such as a sound file, an image, but not code) in your project. There is some minor bureaucracy involved with that.

Every asset (and project on eg github) has a *license* This tell you what you're allowed to use it for. This depends on your usecase: sometimes it's free for educational and commercial use (such as the [MIT license](https://opensource.org/license/mit)). Sometimes it's free for commercial use [such as the GPL license](https://en.wikipedia.org/wiki/GNU_General_Public_License). Basically, you have to check every time if you can use something 

As a deliverable, you *must* have a attribution file listing every asset (or bundle of assets) you use, it's license

### Online version

You are required to make an online version of your pygame. This will be explained in depth during the workshop 'publishing', and it's material will be posted on Toledo. There are things that won't work online (such as a controller or webcam), in that case you need to implement a fallback: an alternative method that does work online such as keyboard controls or a video. In any case, just ask, we can find a solution together.

### Posting on itch.io

As will be explained in detail in the 'publishing' workshop, you will post your game in the projectweek group on [itch.io](http://itch.io/). This way, you can easily link your game to let your friends play, or to put it on your CV in the future

## Seeking help

While there is no well defined path to follow after the initial steps, that doesn't mean you're left to figure it out on your own. We will have plenty of people in the hemisfeer, either in front waiting for questions, or walking around.

### Lecturers

Feel free to ask us anything about the your game, game programming, or the projectweek in general. Or don't ask us anything, tell us about your game!

### 2nd year students

Especially feel free to talk to them for any problems you might have, or advice about coding, git, quality of your game, and especially git :)

### 3d year students

There will probably be some 3rd year students in front from the course Extended Reality. You can recognize them by the VR headset on their head and the dark rings under their eyes. They're here because we don't have that many headsets, and they can't use them over the xmas break. 

In general, please don't disturb them, especially if they're programming/look concentrated. However, they might ask you to try their project (they need to do a user study). In that case, feel free to ask them as much as you want.

### Online
* The stories and documentation of this project can be found here : [projectweek.leone](http://projectweek.leone.ucll.be/overview.html). 
* The [sample pack](https://github.com/harveypekar/pygame-samples) is a WIP projecd withs many little programs demonstrating an aspect of game development. How to play a sound, how to read a key from the keyboard... If you feel like you could use a sample that's not in their, let us know
* The [official pygame documentation](https://www.pygame.org/docs/) is a logical place to look, and it has links to external tutorials
* If video is more your thing, we use [How to Program a Blackjack Game With Python](https://www.youtube.com/watch?v=e3YkdOXhFpQ) for the remote track of introduction project. Try to be efficient with your time: no need to pause the video and type the code he's writing. You can find final code [on Github](https://github.com/plemaster01/pygameBlackjack). Remote students *really* love his content, so check out his channel for more pygame and other stuff.

## Theme

Game jams often have a theme. This theme is a way to give you some guidance when choosing what your game is about. More importantly, the theme is  **optional**, you can totally ignore it if you want.

The theme of the project week is drumroll.....


******************************
*                            *
*     !!!  MERGING  !!!      *
*                            *
******************************

Why would this help you? Think of all the scenario's where we use the word merging:

* Cars merge when two lanes turn into one 
* Two companies can merge and become a single company
* Two rivers can merge

How does this help us? Think of those scenarios, and try to come up with a way to make a game out of them

* A game where there's a busy lane, and you need to drive a car into a gap to merge
* A game where you run a merger of a university and trash collection company
* A game where you have multiple rivers, and you need to divert/merge them to solve a puzzle

It's a lot easier than "lets come up with an idea without any restrictions"

If you don't like the theme, try to think of another way to focus your creativity

* Look at your hobbies. For example, volleyball. You can make a volleyball game. But that is a bit uninspiring. What about a volleyball game where you're superstrong, and hit cars to merge them?
* Read the news. There's a ton of different topics, maybe it pokes your brain into an idea
* Think of games you've already played. For example, Fortnite. Now, add the word 'but'. Think "Fortnite, but..." and try to finish the sentence

