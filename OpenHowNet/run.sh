#!/bin/bash
cat dict_data_zipped/dict.tar* > dict.tar
tar -xf dict.tar
cat pack_zipped/pack.tar* > pack.tar
tar -xf pack.tar
mv dict_data/* ./
rm dict.tar pack.tar
