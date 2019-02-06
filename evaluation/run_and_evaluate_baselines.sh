#!/bin/bash

data=( 'full' 'partial' )
extraction='auto'
#extraction='gold'
combine=( 'exact' 'noclash' )
#props=( 'p0' 'p1' 'p2' 'p3' 'p4' 'p5' 'p6' 'p7' 'p8' 'p9' 'p10' )
props=( 'p11' )

baseline="name_students_baseline"

cd ../systems

for cmb in "${combine[@]}" ; do
	for which_data in "${data[@]}" ; do
		for which_props in "${props[@]}"; do
			echo "\n$extraction $which_data $cmb $which_props"
			system_dir="${extraction}/${which_data}/${cmb}/${which_props}"
			mkdir -p "../data/system/${system_dir}"


			python3 cluster.py -p $which_data -e $extraction -m $cmb -c $which_props
			python3 ../evaluation/evaluate.py -p $which_data -s $system_dir
		done
	done
done

cd ../evaluation
