# TAQQUEST
### Video Demo:  <https://www.youtube.com/watch?v=52Q00Gw1P_g>
### Description:

Taqquest is a customizable Flask web-based application for students and educators alike to assist learners where the final examination/test is multiple-choice format. Repeated self-testing aids in deepening understanding, and identifying knowledge gaps.

"Taqquest" combines the Japanese word for "Real Estate" (_takuchi_) with the english word "Question"/"Quest"


### Features:

- Web-based application which stores User's past performance to ascertain progress and areas needing improvement
- Database of past year's tests allows Users to check their own understanding level based on actual questions
- Past year's tests can be uploaded to the database, and can be changed or added to if needed
- GUI allowing User's to quickly access individual questions from any of past year's tests
- Links to online explanatory material provided with each question

### Objective:

The objective of project was to create an online environment where learners can quickly and easily test themselves using actual questions from previous tests. This project uses the Japanese Real Estate Agent licensing test, which is an annually held test, of 50 multiple-choice questions. The fact the format and number of questions does not change each year makes this test particularly suited to this project, however the project is customizable to be able to accomodate variation from this format.

Simple, mouse/touch-based GUI was desired for ease of use, and the absence of written/long-form questions in the Japanese Real Estate Agent licensing test.

### Registration & Log-in
A new User registers in the Users table of the database, allowing the database to keep track of previous answer attempts. The User can then log-in again at a later date and previous performance will be displayed in the "performance-matrix", while having new attempts aggregated also.

The project referenced the "Finance" project of cs50 for Registration and Log-in pages.

### Question selection
The application consists of one main screen for simplicity. Users select the test Year and the question from that Year on which they wish to test themselves.
Once the question has been selected, the question and answer choices are displayed. Additional information for the question can also be displayed between the question and answer choices.

A link to external resources for each question also appears should the User wish to research the question further.

### Answer selection
Once the User selects their desired answer from the list of possible answers, the application records the answer under the User's record, and checks the database whether the answer is correct or not.
If correct, the word "Correct" is displayed and the date (coloured Green) is added to a list of historic attempts displayed on the question screen.
If incorrect, the word "Incorrect" is displayed and the date (coloured Red) is added to the list.
A percentage calucating the User's performance on this question is also displayed, and the "performance-matrix" colour is updated, if necessary.

### Navigation
To easily and quickly navigate to different questions, several options are provided.
- Selecting Year and Question from the buttons at the top of the screen
- Using "Next" or "Previous" to go back or forward in order. The "Random" option will display a random question from the Problem table.
- Each question in the "performance-matrix" is clickable, meaning one-click access to any question in the Problem table.

### Performance-matrix
The "performance-matrix" is a display representing every question in the Problem table and the current User's past performance on that question, as indicated by a colour (Green/Yellow/Red). Each question in the "performance-matrix" is clickable, meaning Users can quickly access any question in the Problem table with one click.

### Log-out
The current User can log-out at any time using the "Log-out (user)" link at the top of the screen, which returns the application to the Log-in screen.

### Files included and uses

- app.py - flask application file
- testprobs.db - Database containing tables:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Problems - stores the question list\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Users - stores registered Users\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;results - stores a list of answer attempts by Users, datetime and Correct/Incorrect for evaluation




#### As the main display page changes according to the User's selection, the application uses Jinja to insert new sections as needed

#### Directory

/templates
- layout.html - main display page including Head, Body and apology splash-section
- login.html - login page
- questions.html - displays question buttons, Next/Prev/Random navigation buttons, and "performance-matrix"
- register.html - registration page
- selection.html - displays question and answer content, and a list of dates of previous attempts, coloured according to Correct/Incorrect
- years.html - displays year buttons

/static
- chocot.png  - apology splash-section graphic
- favicon.ico - creator favicon
- style.css - style sheet




### Error handling
Should a User select a Year and then "Next" or "Previous", an apology splash-section will display to instruct the User to "Please select a Year"


