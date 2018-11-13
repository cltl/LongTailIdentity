data=( 'full' 'partial' )
for which_data in "${data[@]}" ; do
	#python3 name_students_baseline.py -p full
	python3 noclash_baseline.py -p $which_data
	python3 ../data_preparation/evaluate.py -p $which_data -s name_students_baseline
done
