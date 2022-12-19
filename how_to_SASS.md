# How To :: Use SCSS (SASS)
## (**S**yntactically **A**wesome **S**tyle**s**heet)
---
### **Chronically Late**
#### Estimated Time: 30 min.
---
## Overview:
SASS is a preprocessor[^1] language that is interpreted as CSS. It is an extension to CSS.

In SASS, there are many useful features that exist that don't in CSS, such as variables, nested loops, inheritance, functions, etc. Because of that, many people find it useful to write SASS code and compile it as CSS because it is more efficient for some website-building aspects. 

*SASS files have the `.scss` file extension

### Prerequisites:

### Steps:
1. In your `\static` folder (for your CSS files), make a stylesheet under the `.scss` extension
2. Write your SASS code

To Compile:
1. Download SASS (https://sass-lang.com/install)
2. Run `sass source/stylesheets/index.scss build/stylesheets/index.css`
3. Now you have a readable CSS file!

### Syntax Examples:
#### commenting
- `/* comment */`
- `// comment`
#### store a variable with `$` 
- EX: ```$red: #FF0000;` stores the hex code for red as a variable "red"
- can use the variable by calling `$red` again
#### loops
1. @each
- `@each $<thing> in $<listOfThings> {<doThis>;}`
2. @for
- `@for $<variable> from <num> through <num> {<doThis>;}`

### Resources:
- https://www.w3schools.com/sass/sass_intro.php
  (w3 schools introduction to SASS)
- https://sass-lang.com/documentation/at-rules/control/for
  (for loop documentation)
- https://sass-lang.com/documentation/at-rules/control/each
  (each loop documentation)
  
---
Accurate as of last update: 2022-12-18

#### Contributors:
Jasmine Yuen, pd2
---
[^1]: program that takes in input data to process and produce an output that is readable for another program