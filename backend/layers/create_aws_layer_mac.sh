#!/bin/bash

# Define variables
REQUIREMENTS_FILE="layer_requirements.txt"

# Delete all zip files in the current directory
echo "Deleting all existing .zip files in the folder..."
rm -f *.zip

# Read the requirements file line by line
while IFS= read -r package
do
  # Skip empty lines and comments
  [[ -z "$package" || "$package" == \#* ]] && continue

  # Remove any leading/trailing whitespace and carriage return characters
  package=$(echo "$package" | tr -d '\r' | xargs)

  # Define directories and files for each package
  LAYER_NAME="${package//\//_}" 
  PACKAGE_DIR="python"  # Create 'python' folder inside the package folder
  ZIP_FILE="$LAYER_NAME.zip"  # Zip file will be named after the package

  # Clean up any existing folder and zip file
  rm -rf "$LAYER_NAME" "$ZIP_FILE"

  # Create the necessary directory structure
  mkdir -p "$PACKAGE_DIR"

  # Install the package and its dependencies into the layer directory
  echo "Installing package: $package"
  pip install --target="$PACKAGE_DIR" "$package" --no-user --no-cache-dir

  # Ensure the 'python' directory exists before zipping
  if [ ! -d "$PACKAGE_DIR" ]; then
    echo "Error: '$PACKAGE_DIR' not found after pip install for package $package."
    continue
  fi

  # Use the zip command to create the zip file on macOS
  echo "Creating zip file for $package..."
  zip -r "$ZIP_FILE" "$PACKAGE_DIR" > /dev/null

  # Check if the zip was successful
  if [ $? -eq 0 ]; then
    echo "$package Lambda layer package $ZIP_FILE created successfully."
  else
    echo "Error creating zip file for $package."
  fi

  # Clean up by removing the folder used to create the zip
  rm -rf "$PACKAGE_DIR"

done < "$REQUIREMENTS_FILE"
