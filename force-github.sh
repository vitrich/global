#!/bin/bash
echo "🚀 НАСИЛЬНАЯ ЗАГРУЗКА на GitHub $(date)"

# 1. .gitignore (только мусор)
cat > .gitignore << GITIGNORE
__pycache__/
venv/
db.sqlite3
media/
static/
*.pyc
*.log
.env
passenger_wsgi.py
GITIGNORE

# 2. Очистить Git кэш (ВСЁ!)
git rm -r --cached . 2>/dev/null || true

# 3. Добавить ВСЕ файлы проекта
git add -f .
echo "📁 Добавлено файлов: $(git ls-files | wc -l)"

# 4. Коммит
git commit -m "Force upload: полный Django CMS + grade5 $(date)"

# 5. НАСИЛЬНЫЙ PUSH (перезапишет GitHub!)
git push origin main --force

echo "✅ GitHub: https://github.com/vitrich/letovo"
