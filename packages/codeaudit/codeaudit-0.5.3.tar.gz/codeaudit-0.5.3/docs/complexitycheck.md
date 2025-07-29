# A Simple Cyclomatic complexity Check

[Cyclomatic complexity](https://en.wikipedia.org/wiki/Cyclomatic_complexity) is a software metric used to indicate the complexity of a program. It was developed by Thomas J. McCabe, Sr. in 1976. 

But truth is: Calculating the Cyclomatic complexity for Python sources is rather complex to do right. This comes partly because it is opinionated. 

So I decided to take a more pragmatic and simple approach. So the goal of the Simple Complexity Score is to get a 'calculated' number that gives that gives a **good and solid** representation for the complexity of a Python source file.

So the code created gives an accurate, but not exhaustive cyclomatic complexity measurement. 

The complexity is determined per file, and not per function within a Python source file. I have worked long ago with companies that calculated [function points](https://en.wikipedia.org/wiki/Function_point) for software that needed to be created or adjusted. Truth is: Calculating exact metrics about complexity for software code projects is a lot of work, is seldom done correctly and are seldom used with nowadays devops or scrum development teams. 

But a good indication for the complexity of source code gives a solid indication from a security perspective.
Complex code has a lot of disadvantages when it comes to managing security risks. Making corrections is difficult and errors are easily made.