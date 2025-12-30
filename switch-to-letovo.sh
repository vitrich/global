#!/bin/bash
cd /home/c/co53144/cms/public_html/

echo "🔄 Переключение на vitrich/letovo.git"

# 1. Новый remote
git remote set-url origin git@github.com:vitrich/letovo.git

# 2. Проверить статус
echo "Remote: $(git remote get-url origin)"

# 3. Push
git push origin main --force

echo "✅ letovo: https://github.com/vitrich/letovo"
echo "📁 Файлов: $(git ls-files | wc -l)"
