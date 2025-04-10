#!/bin/bash

REQUIREMENTS_FILE="layer_requirements.txt"

echo "Deleting all existing .zip files in the folder..."
rm -f *.zip

while IFS= read -r package
do
  [[ -z "$package" || "$package" == \#* ]] && continue

  package=$(echo "$package" | tr -d '\r' | xargs)

  LAYER_NAME="${package//\//_}" 
  PACKAGE_DIR="python"
  ZIP_FILE="$LAYER_NAME.zip"

  rm -rf "$LAYER_NAME" "$ZIP_FILE"

  mkdir -p "$PACKAGE_DIR"

  echo "Installing package: $package"
  pip install --target="$PACKAGE_DIR" "$package" --no-user --no-cache-dir

  if [ ! -d "$PACKAGE_DIR" ]; then
    echo "Error: '$PACKAGE_DIR' not found after pip install for package $package."
    continue
  fi

  echo "Creating zip file for $package..."
  zip -r "$ZIP_FILE" "$PACKAGE_DIR" > /dev/null

  if [ $? -eq 0 ]; then
    echo "$package Lambda layer package $ZIP_FILE created successfully."
  else
    echo "Error creating zip file for $package."
  fi

  rm -rf "$PACKAGE_DIR"

done < "$REQUIREMENTS_FILE"

echo "Setting up Node.js layer with aws-jwt-verify..."
NODE_LAYER_DIR="nodejs"
NODE_ZIP_FILE="authorizer.zip"

rm -rf "$NODE_LAYER_DIR" "$NODE_ZIP_FILE"

mkdir -p "$NODE_LAYER_DIR"
cd "$NODE_LAYER_DIR"

npm init -y
npm install aws-jwt-verify

cd ..

zip -r "$NODE_ZIP_FILE" "$NODE_LAYER_DIR" > /dev/null

if [ $? -eq 0 ]; then
  echo "Node.js Lambda layer package $NODE_ZIP_FILE created successfully."
else
  echo "Error creating Node.js zip file."
fi

rm -rf "$NODE_LAYER_DIR"