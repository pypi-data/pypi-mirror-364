---
description: Fetch and analyze remote or local repositories using repo-to-md
allowed-tools: [Bash, Write, Read]
---

# Fetch Repository Content

Use this command to fetch and analyze repository contents from GitHub or local paths using the `repo-to-md` tool.

## Usage Examples

### Fetch entire repository to context
```
/fetch-repo owner/repo
```

### Fetch specific branch
```
/fetch-repo owner/repo --branch develop
```

### Fetch with include/exclude patterns
```
/fetch-repo owner/repo --include "src/" --exclude "*.lock"
```

### Fetch to local file
```
/fetch-repo owner/repo --output repository-analysis.md
```

### Fetch local repository
```
/fetch-repo /path/to/local/repo
```

---

I'll analyze the repository content using repo-to-md with the following arguments: $ARGUMENTS

Let me fetch the repository content:

```bash
repo-to-md $ARGUMENTS
```

The repository content has been fetched. I can now analyze the code structure, implementation patterns, and provide insights about how specific features are implemented in this codebase.

Would you like me to:
1. Analyze specific implementation patterns?
2. Extract particular code sections?
3. Compare with other approaches?
4. Save the output to a file for further reference?