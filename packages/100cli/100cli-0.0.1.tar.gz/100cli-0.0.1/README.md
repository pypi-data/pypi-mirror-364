<div align="center">

![100cli](./assets/100cli_logo.png)

_🤖 The 100 LoC CLI agent made to be hacked — simple, easy to understand, and hackable ✨_
</div>

CLI Agents are great! I use them all the time. As an avid user of CLI agents like claude code, opencode and more, I needed a simple 100 LoC CLI agent that can be used to easily hack and experiment with about CLI agents. There are many tools to experiment with, flows to provide the agents and new ideas keep coming up every day. We don't really have a simple way to experiment with them.

This project aims to resolve that need.

It doesn't have many features out of the box, but it creates a foundation for anyone to build upon and is available on [GitHub](https://github.com/chonknick/100cli) as a template.

The goals of this project are:

- Remain simple and extensible — have only the core functionality that's widely used and easy to understand.
- Provide a simple and easy-to-use interface for users to interact with the CLI agent.
- Allow users to easily extend the functionality of the CLI agent by adding new features, commands and tools.
- The entire docs should fit on this README.md file. (very important!)

To this end, we choose to write it in Python because it's very easy to write tooling in and you can easily make it performant with C or Rust extensions, if you want to.

## Installation

```
pipx install 100cli
```
