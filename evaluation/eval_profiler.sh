extractors=( 'auto' 'gold' ) 
data=( 'partial' 'full' )

for extractor in "${extractors[@]}" ; do
    for which_data in "${data[@]}" ; do
        python evaluate.py -s "${extractor}_profiling/${which_data}" -p "${which_data}"
    done
done
