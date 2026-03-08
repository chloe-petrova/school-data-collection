# Intent

## What I Want to Build

I want to build a tool that runs locally on my computer and uses AI to automatically scrape and monitor school websites. It is a personal tool, built entirely for my own use.

When I run it manually, an AI agent takes over and works through the school websites autonomously — browsing pages, pulling out relevant information, and deciding what to collect based on what it finds. The agent handles the multi-step process on its own rather than me having to do it manually each time.

All of the data the agent collects gets stored and logged so I can look back at it later. The goal is to have a reliable record of information gathered from school websites without me having to do the work of visiting them, reading through them, and saving things by hand.

## What Information to Collect

For each school, the tool should find and record the following four things:

1. The name of the head (headteacher or principal)
2. The email address of the head
3. The name of the safeguarding lead
4. The email address of the safeguarding lead

If a direct email address for the head or safeguarding lead is not published on the website, the agent should fall back to the best available general contact email for the school (such as a main office or admin address). The names of the head and safeguarding lead should always be captured regardless of whether an email is found.

## The Problem It Solves

School websites contain information I care about but checking them manually takes time and effort. This tool automates that process — I kick it off, the AI figures out what is on the pages and what is worth keeping, and the results get saved somewhere I can reference.

## How It Works (Plain English)

1. I run the tool myself when I want to collect information.
2. The AI agent starts browsing the school website or websites.
3. It works through the pages autonomously, deciding what to read and what to capture.
4. Everything it finds gets logged and stored on my computer for later use.

## Scope

This is a simple, personal, locally-run utility. It does not need a user interface, a hosted server, or any kind of sharing or collaboration features. It just needs to work reliably for me on my machine.
