# Dynamic Project Environment Implementation Plan

## Investigation Summary
**Status**: ❌ Feature NOT currently implemented  
**Branch Created**: `feature/dynamic-project-environment`

## Current Limitations Found

### 1. exec.py (plugins/system/exec.py)
```python
# Line 81-88: No environment parameter
result = subprocess.run(
    command,
    shell=True,
    capture_output=True,
    text=True,
    timeout=timeout,
    cwd=working_dir
)
# Missing: env=project_environment
```

### 2. activate.py (plugins/system/activate.py)  
- Only changes directory with `os.chdir()`
- Does NOT load .env files
- No environment variable management

### 3. No Environment Manager
- No ProjectEnvironmentManager class exists
- No .env file loading capability
- env.py tool only modifies current process

## Implementation Roadmap

### Phase 1: Create Environment Manager
Create `lib/env_manager.py`:
```python
class ProjectEnvironmentManager:
    def __init__(self):
        self.base_env = os.environ.copy()
        self.project_envs = {}
        self.active_project = None
    
    def load_project_env(self, project_name, project_path):
        """Load .env file from project directory"""
        
    def get_merged_env(self):
        """Return base + project environment"""
```

### Phase 2: Enhance activate.py
```python
# Add to activate.py execute():
# Load project environment
env_manager.load_project_env(project_name, project_path)
```

### Phase 3: Enhance exec.py
```python
# Modify subprocess.run call:
env = self.session_manager.env_manager.get_merged_env()
result = subprocess.run(
    command,
    shell=True,
    capture_output=True,
    text=True,
    timeout=timeout,
    cwd=working_dir,
    env=env  # ADD THIS
)
```

### Phase 4: Update SessionManager
Add environment manager to `core/manager.py`:
```python
def __init__(self):
    # ... existing code ...
    self.env_manager = ProjectEnvironmentManager()
```

## Expected Behavior After Implementation

```bash
# User activates project
> activate ics
✅ Project 'ics' activated
✅ Loaded 5 environment variables from /var/projects/ICS/.env

# Exec commands get project environment
> exec echo $DATABASE_URL
postgresql://ics_user@localhost/ics_db  # ICS-specific

# But bash sessions keep global environment  
> bash
$ echo $DATABASE_URL
(empty or global value)
```

## Benefits
- ✅ Dynamic project switching at runtime
- ✅ No pre-configuration needed
- ✅ Project-specific secrets for exec commands
- ✅ Backwards compatible (PTY sessions unchanged)
- ✅ Follows architectural constraints

## Next Steps
1. Implement ProjectEnvironmentManager
2. Enhance activate.py to load .env
3. Enhance exec.py to use project environment
4. Test with multiple projects
5. Create PR for review