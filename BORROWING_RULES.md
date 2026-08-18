# Seed Borrowing Rules

Seed may learn from open-source projects, but must not become an unreviewed clone.

Rules:
1. Check the license before copying code.
2. Prefer borrowing architecture patterns before copying code.
3. Keep third-party repos inside third_party_repos/, ignored by Git.
4. Document every borrowed idea in THIRD_PARTY_NOTES.md.
5. Never copy credential handling, auto-execution, or unsafe computer-control code blindly.
6. Any self-editing or system action must remain approval-gated.
7. Borrowed code must be small, understood, and adapted to Seed's architecture.
8. Seed remains local-first, private, readable, and controlled by User.