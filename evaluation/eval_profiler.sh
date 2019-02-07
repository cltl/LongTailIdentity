extractors=( 'auto' 'gold' ) 

for extractor in "${extractors[@]}" ; do
	#python evaluate.py -s "${extractor}_profiling/partial" -p partial
        python evaluate.py -s "${extractor}_profiling/full" -p full
done
