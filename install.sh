#!/bin/bash

rm -rf cloudlens-cli
url="https://github.com/OpenIxia/CloudLens-cli"
git clone "$url" > /dev/null 2>&1

(
    cd "${HOME}"
    rm -rf ".cloudlens-cli"
    mkdir ".cloudlens-cli"
)

mv cloudlens-cli/* ${HOME}/.cloudlens-cli
rm -rf cloudlens-cli

(
    cd "${HOME}"
    chmod +x "${HOME}/.cloudlens-cli/cloudlens.py"
    chmod +x "${HOME}/.cloudlens-cli/deployment/"*.sh
)

if [ ! -d "/usr/local/bin" ]; then
    echo "/usr/local/bin does not exist. Might need sudo permissions to create directory"
    echo ""
    sudo mkdir -p "/usr/local/bin"
fi

if ! [ -L "/usr/local/bin/cloudlens" ]; then
    echo "Creating symlink..."
    ln -s "${HOME}/.cloudlens-cli/cloudlens.py" "/usr/local/bin/cloudlens"
    echo "Symlink created successfully"
    echo ""
fi

green='\033[0;32m'
lblue='\033[1;34m'
cyan='\033[0;37m'
nc='\033[0m'

echo ""
echo -e " *****************************************************************************************"
echo -e " *                                                                                       *"
echo -e " *  ${green}CloudLens CLI was successfully installed${nc} 🎉                                          *"
echo -e " *                                                                                       *"
echo -e " *  Now you can run:                                                                     *"
echo -e " *                                                                                       *"
echo -e " *  ${lblue}  cloudlens -h                    ${nc}# help                                             *"
echo -e " *  ${lblue}  cloudlens start webhook         ${nc}# activates webhook                                *"
echo -e " *  ${lblue}  cloudlens start testapp         ${nc}# deploys test sleep app with sidecar injection    *"
echo -e " *                                      in the current namespace                         *"
echo -e " *  ${lblue}  cloudlens status                ${nc}# checks the current state of the webhook and      *"
echo -e " *                                      of any deployed cloudlens instances              *"
echo -e " *  ${lblue}  cloudlens shutdown webhook      ${nc}# shutdown the webhook                             *"
echo -e " *  ${lblue}  cloudlens shutdown testapp      ${nc}# remove the test sleep app                        *"
echo -e " *  ${lblue}  cloudlens uninstall             ${nc}# uninstall cloudlens cli                          *"
echo -e " *                                                                                       *"
echo -e " *                                                                                       *"
echo -e " *****************************************************************************************"

