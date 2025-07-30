# What is CAT?

Automate tests for your data! CAT is a simple tool that helps you to automate tests for your data.


🐱 Compare data accross systems (e.g. SQL server with Power BI)

🐱 Easy configuration for tests, no learning curve

🐱 Install in one minute, first tests in a few minutes

🐱 Free for interactive* use (even for production data)

🐱 Automation friendly (Azure DevOps, GitLab, ...)

🐱 Desktop app, CLI, PowerShell module, Python package


* *Scheduled runs, CI/CD pipelines etc. require a license*

<br />

To get started quickly and easily, follow the tutorial in our docs:

https://docs.justcat.it/docs/get-started/python-module/install/

<br />

# Prerequisites

* You need to have [.NET 8 runtime](https://dotnet.microsoft.com/en-us/download/dotnet/8.0) installed in order to use this package.

* We depend on pythonnet package. If you cannot install it for any reason, you'll not succeed to use CAT package either.

# Considerations

The core of CAT software is written using .NET. This package is a "wrapper". We try to make your experience as much as possible "Python-like", but you may encounter 

* C# naming conventions in returned types (such as in test definitions, test results etc.)

* .NET objects e.g., for collections.

It is not a problem, but if you think it is, you can still run CAT tests with one line of code and then work with JSON output (it contains just everything about the tests).



# Links

* Home page: <a href="https://justcat.it">https://justcat.it</a>
* Documentation: <a href="https://docs.justcat.it">https://docs.justcat.it</a>

<br />



**HAPPY TESTING!**<br />
CAT team