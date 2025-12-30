#!/bin/bash
cd /home/c/co53144/cms/public_html/

echo "🚀 Принудительная отправка всего проекта"

# Очистка
git rm -r --cached . 2>/dev/null || true

# .gitignore
cat > .gitignore << GITIGNORE
__pycache__/
venv/
db.sqlite3
media/
static/
*.pyc
.env
GITIGNORE

# Добавление ВСЕГО
git add -f .
echo "Добавлено файлов: $(git ls-files | wc -l)"

# Коммит + push
git commit -m "Full project: Django CMS + grade5 $(date)"
git push origin main --force

echo "✅ Проверьте: https://github.com/vitrich/grade5"
