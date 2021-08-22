# Ensure we have the correct permissions on the hs dir, or Tor won't run
chmod 700 shadow.data.template/hosts/hiddenserver/hs
# Run the Tor minimal test and store output in shadow.log
rm -rf shadow.data
rm -rf /home/lorenzo/Documents/tesi/testshadow/pcaps/*
rm -f ./pairs.log

python3 ./generate_config.py $1 $2

for ((i = 0 ; i <= $1 ; i++)); do
  cp -r ./shadow.data.template/hosts/torclient ./shadow.data.template/hosts/torclient$i
done

shadow --template-directory shadow.data.template shadow.yaml > shadow.log

./convert.sh

notify-send finito
