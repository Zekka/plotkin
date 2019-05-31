# plotkin

Experiments in porting the Inform type system to Rust, via a Python program 
that generates the relevant types.

In any case where I've got to choose between faithfulness to Inform and Rust
ergonomics, I'll pick Rust ergonomics.

You can play with it if you want -- see `main.py` for a convincing example.

However, it's just a hack.

## Usage

Edit `main.py` to reflect your project, then run it. Consider creating your
project with Cargo first. (it will overwrite existing files but doesn't 
generate any that overlap a default cargo project.)

You should add the `world` module to `main.rs` in order to load the generated
code.

Ideally you should make all requirements available in a venv. (by installing
requirements.txt) I have only tested my code on Python 3.7, but I expect my
code will probably work on Python 3.6 and Python 3.8 too.

## Why?

Inform has a great type system for video game content -- each instance has its
own type and you can comprehense over all the items of a type. Each is 
effectively global.

## Progress

Things I did:

- things (renamed to "entities") and kinds 
- actions

Things I didn't do yet:

- *meaningful* examples
- relations
- string-generating procedures
- literally any parsing

A lot of stuff is pretty impoverished. Also, there are no tests -- my testing
methodology is "run main.py, then see if the resulting Rust code compiles."

You really shouldn't use this yet.

## Contributing

I'll read your code if you make a pull request, but you should really contact
me in advance.

Please run `black` on default settings to format your code.

## Note

Named for Andrew Plotkin, one of the three Inform 7 designers (the other two
being Graham Nelson and Emily Short.)
