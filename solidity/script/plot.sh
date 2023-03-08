ALGOUTPUTDIR=$1

python3 plots/plot_error_var_alpha.py --K 3 --alg_output_dir $ALGOUTPUTDIR
python3 plots/plot_error_var_alpha.py --K 4 --alg_output_dir $ALGOUTPUTDIR
python3 plots/plot_error_var_alpha.py --K 5 --alg_output_dir $ALGOUTPUTDIR
python3 plots/plot_acc.py --output_dir output/acon2_K_3_alpha_0d01_iter_1_duration_3600 --exp_name "" --tag K_3_alpha_0d01_iter_1 --alg_output_dir ${ALGOUTPUTDIR}/acon2_K_3_alpha_0d01_iter_1_duration_3600
python3 plots/plot_error.py --alg_output_dir $ALGOUTPUTDIR

echo ""
python3 plots/plot_gastab.py --alg_output_dir $ALGOUTPUTDIR
