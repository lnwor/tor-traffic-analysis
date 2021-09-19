# Ensure we have the correct permissions on the hs dir, or Tor won't run
chmod 700 shadow.data.template/hosts/hiddenserver/hs
# Run the Tor minimal test and store output in shadow.log
rm -rf shadow.data
rm -rf /run/media/Documents/pcaps/*
rm -f ./pairs.log

python3 ./generate_config.py $1 $2

for ((i = 0 ; i <= $1 ; i++)); do
  cp -r ./shadow.data.template/hosts/torclient ./shadow.data.template/hosts/torclient$i
done

shadow --template-directory shadow.data.template shadow.yaml > shadow.log

./convert.sh

./anal10.py >> analysis.log
./anal20.py >> analysis.log
./anal30.py >> analysis.log
./anal40.py >> analysis.log
./anal50.py >> analysis.log
./anal60.py >> analysis.log
./anal70.py >> analysis.log
./anal80.py >> analysis.log
./anal90.py >> analysis.log
./anal100.py >> analysis.log
