This document describes our rules for documenting things

## The Rules

1. Remember that all our documentation is public-facing.
2. All engineering documentation in its final state must live in GitHub.
3. Draft / WIP engineering documentation can live in Google Drive if desired
4. Code documenation of 3 paragraphs or longer must go into a `.md` file in the same location as the code. You must be able to find every engineering `.md` file via "walking down" links from the root README.md of the repository. Which is to say, add a link from `DEVELOPEMENT.md` or `OPERATIONS.md` or `README.md` (any of them, there are several) into your new `.md` file.
6. Code comments of 1 paragraph of longer, or otherwise sufficiently complex, must be linked to from a `.md` file, any `.md` file, pick whichever one makes the most sense.
7. When documenting AWS, the written and screenshot documentation must have all sensitive / unique / secrets information redacted, including but not limited to:

  - secrets
  - unique id's / UUIDs
  - information that is unique to a given user
  - anything related to IAM

7. AWS links and screenshots that only contain a generic URL (ex. https://us-east-1.console.aws.amazon.com/rds/home?region=us-east-1#databases) and generic names visible on the screen (eg. simply `api-dev` without any attached unique IDs) are generally safe. If in doubt, don't include it.
8. Architecture diagrams go into Github. A link into the source drafting tool for the architecture diagram must be added as well, like for example Lucid Chart.
9. Github issues / PRs documenting durable information of 3 paragraphs of longer, or of sufficient complexity or value, must be linked to from a `.md` file.
10. Avoid linking into the repo's root README.md file if at all reasonable. 
11. Always prefer documentation living close to its code, rather than inside of the `documentation/` folder. Tech specs / preliminary design documentation is the exception to this. If in doubt:

  - Documentation created before code is written may go inside of `documentation/`
  - Documentation created after code is written should not go inside of `documentation/`

12. Meta documents (such as this one) must also follow these rules.
13. These rules only apply to engineering documentation. 
14. These rules should be actively enforced. Which is to say: request changes inside of PRs that don't follow these rules.
15. This document has no opinion about when something should be documentation, only how and where it should be documented.
16. This is a lot of rules so don't be rude if someone forgets some of them.
