---
name: create-user-story
description: Use this skill to help turn your ideas into well-structured user stories that can be easily understood and implemented by development teams.
---

# Create User Story

Parse the user input and create a user story, written as local markdown file.

## Process

### 1. Gather Information

Parse the user input and ask follow-up questions to gather the necessary information to create a user story. This includes understanding the user's needs, the problem they are trying to solve, and the value they expect to gain from the solution.

Ask the user for the following information if it could not be determined from the initial input:

- **Type of user**: Who is the user that will benefit from this feature? (e.g. "As a [type of user]")
- **Action**: What action does the user want to perform? (e.g. "I want [an action]")
- **Benefit**: What is the benefit or value that the user will gain from this action? (e.g. "so that [a benefit]")

### 2. Create the user story

Once you have gathered all the necessary information, create a user story in the following format:
`As a [type of user], I want [an action] so that [a benefit].`

### 3. Write the user story to markdown

Write the primary user story to `artifacts/user-stories/`. Use a naming pattern that includes the user story number and a short descriptive title (e.g. `artifacts/user-stories/001-add-login-feature.md`).

If the conversation produces meaningful supporting context beyond what is already captured (for example clarifications, constraints, or design decisions), write that context to the file using title in the markdown file `# Additional Context`.

Where `{story}` is the base name of the primary story file without the `.md` extension.

Only create the companion file when there is meaningful additional context worth preserving.
