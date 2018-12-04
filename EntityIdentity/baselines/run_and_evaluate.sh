data=( 'full' 'partial' )
extraction='auto'
combine=( 'exact' 'noclash' )

for cmb in "${combine[@]}" ; do
	for which_data in "${data[@]}" ; do
		echo "$which_data $cmb"
		python3 cluster.py -p $which_data -e $extraction -m $cmb
        
		python3 ../data_preparation/evaluate.py -p $which_data -s auto_ext_baseline
	done
done
