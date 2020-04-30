cat pack_zipped/pack.tar* > pack.tar
cat dict_data_zipped/dict.tar* > dict.tar
tar -xf pack.tar
tar -xf dict.tar
mv dict_data/* ./

