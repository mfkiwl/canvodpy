#!/bin/bash
# Git History Search for RINEX304Validator

echo "=========================================="
echo "Searching Git History for RINEX304Validator"
echo "=========================================="

echo ""
echo "1. Search for file 'validators.py' in gnss_specs directory:"
git log --all --full-history -- "*/gnss_specs/validators.py"

echo ""
echo "2. Search for any file containing 'validators' in gnss_specs:"
git log --all --full-history -- "*/gnss_specs/*validator*"

echo ""
echo "3. Search commits mentioning RINEX304Validator in commit messages:"
git log --all --grep="RINEX304Validator" --oneline

echo ""
echo "4. Search commits mentioning 'validator' in gnss_specs context:"
git log --all --grep="validator" --grep="gnss_specs" --oneline

echo ""
echo "5. Search for RINEX304Validator in code across all commits:"
git log -S "RINEX304Validator" --source --all --oneline

echo ""
echo "6. Search for 'class RINEX304Validator' across all commits:"
git log -S "class RINEX304Validator" --source --all --oneline

echo ""
echo "7. Search for import statement across all commits:"
git log -S "from canvod.readers.gnss_specs.validators import" --source --all --oneline

echo ""
echo "8. Show files changed in commits mentioning validator:"
git log --all --name-only --grep="validator" -- "packages/canvod-readers/*" | head -100

echo ""
echo "=========================================="
echo "Done"
echo "=========================================="
