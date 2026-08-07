# Hermes 工作区 .gitignore 模板
# 用法：复制到 ~/Documents/Hermes/.gitignore
#
# 验证：git check-ignore -v <path>
# 排查：git check-ignore -v --no-index <path>  （检查某路径是否被规则命中）

# Hermes runtime
.hermes/

# Git worktrees
.worktrees/

# Backups
backups/

# Logs
*.log

# Blender backups
*.blend1

# Python cache
__pycache__/

# Data directories (alist etc.)
data/

# Lockfile (auto-generated)
skills-lock.json
