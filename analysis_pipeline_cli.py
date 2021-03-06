"""
This script is a command line interface for running the fiber photometry analysis pipeline
"""


from analysis_pipeline import *

print('==========================================================================')
print('=================fiber-photometry analysis pipeline=======================')
print('============================Alhadeff Lab==================================')
print('==================Monell Chemical Senses Center===========================')
print('==========================================================================')
print(' ')

ans=int(input('Would you like to 1. load and add to an existing analysis or 2. start a new analysis? [1/2]: '))
norm_methods=[norm_to_median_pre_stim, norm_to_405]

if ans==1:
    #load in the analysis from the specified file in the output folder
        fname=input('Please enter the path to an exported analysis file: ')
        a=load_analysis(fname)
else:
    #ask for necessary parameters for the analysis
    t_endrec = input('Enter length of recording in seconds from the stimulus time: ')
    t_endrec = float(t_endrec)

    norm_method=input('How would you like to normalize this data? 1. normalize to the median of pre-stimulus data, 2. normalize to the 405 [1/2]: ')
    norm_method=norm_methods[int(norm_method)-1]

    spec_exc_crit=input('Would you like to specify the exclusion criteria? (i.e. # of st devs above or below the mean of the data beyond which to exclude) [y/n]: ')
    


    if spec_exc_crit.lower() in ['n','no']:
        ex=4
    else:
        ex=int(input('How many st. devs above or below the mean would you like to define as the limits of the data?: '))
    
    spec_prestim=input('Would you like to specify the amount of time pre-stimulus to keep (the default will be 5 minutes)?[y/n]: ')

    if spec_prestim.lower() in ['n','no']:
        t_prestim=300
    else:
        t_prestim=int(input('How many seconds pre-stimulus would you like to keep?: '))
    
    a=analysis(norm_method,t_endrec,ex=ex,t_prestim=t_prestim)

def load_append_save_cli():

    appending=True

    while appending:
        file=Path(input('Please enter the address to an exported data file: ')).resolve()

        if file.suffix=='.json':
            with open(file,'r') as f:
                print('loading data from file...')
                d=json.load(f,object_hook=hook)
        elif file.suffix=='.npy':
            d=np.load(file,allow_pickle=True).tolist()
        else:
            raise Exception('Unrecognized File Format!')

        for i in range(len(d)): #loop through all animal data stored in this run 
            #allow the user to specify the stimulus time in seconds relative to the start of the recording
            d[i].t_stim=float(input(f't_stim for mouse {d[i].mouse_id}:'))
            m=a.normalize_downsample(d[i])
            #allow the user to decide if they'd like to keep the data and store the data in the appropriate place
            if int(input('Would you like to 1. keep or 2. discard this data?[1/2]: '))==1:
                a.raw_data.append(d[i])
                a.normed_data.append(m)
                a.loaded=True
            else:
                a.excluded_raw.append(d[i])
                a.excluded_normed.append(m)

        
        cont=input('Would you like to continue adding?[y/n]').lower()
        if cont in ['n','no'] :
            appending=False
    a.compute_means()
    a.save()

def update_params_cli():

    print('Choose one of the following parameters to update:')
    print('1. Length of the recording')
    print('2. Normalization method')
    print('3. Exclusion criteria')
    print('4. Change File Format')
    print('5. Change Pre-Stimulus Time')
    print('')
    choice=input('(input the number of the desired choice):')

    if choice=='1':
        a.t_endrec = int(input( 'Enter length of recording in seconds from the stimulus time:' ))
    elif choice=='2':
        a.norm_method=norm_methods[int(input( 'How would you like to normalize this data? 1. normalize to the median of pre-stimulus data, 2. normalize to the 405 [1/2]:' ))-1]
    elif choice=='3':
        a.ex=int(input( 'How many st. devs above or below the mean would you like to define as the limits of the data?: ' ))
    elif choice=='4':
        a.file_format=['npy','json'][-1+int(input( 'What file format would you like? 1. npy, 2. json [1/2]: ' ))]
    elif choice=='5':
        a.t_prestim=int(input( 'Enter the desired pre-stimulus time in seconds:' ))
        

def remove_mouse_cli():
    a.remove_mouse(input("Enter the id of the mouse you'd like to remove: "))

def retrieve_excluded_cli():
    a.retrieve_excluded(input("Enter the id of the mouse you'd like to retrieve: "))

def bin_plot_cli():
    a.bin_plot(int(input('How big, in seconds, would you like the bins: ')),save=True)

def bin_auc_cli():
    start=int(input('Enter the beginning of the period in seconds relative to the stimulus onset: '))
    end=int(input('Enter the end of the period: '))
    a.bin_auc(start,end)

def bin_avg_cli():
    start=int(input('Enter the beginning of the period to average in seconds relative to the stimulus onset: '))
    end=int(input('Enter the end of the period: '))
    a.bin_avg(start,end,save=True)

def ind_peak_df_f_cli():
    ans=int(input('Would you like to compute the 1. max or 2. min? [1/2] '))-1
    opts=['max','min']
    a.ind_peak_df_f(opts[ans],save=True)

def mean_peak_df_f_cli():
    ans=int(input('Would you like to compute the 1. max or 2. min? [1/2] '))-1
    opts=['max','min']
    a.mean_peak_df_f(opts[ans],save=True)

running=True
if not a.loaded:
    load_append_save_cli()
    a.plot_both()

while running:
    print('------------------------------------')
    print('Choose one of the following tasks:')
    print('1. plot 490 and 405')
    print('2. plot just the 490')
    print('3. add data to this analysis')
    print('4. save this analysis')
    print('5. find the peak ???f/f (min/max) for individual mice')
    print('6. find the peak ???f/f (min/max) for individual mice at the location of the peak in the mean signal')
    print('7. find the average value over a specified portion of data')
    print('8. find the area under the curve for a specified portion of data')
    print('9. bin and plot the data')
    print('10. remove a mouse from this analysis')
    print('11. retrieve an excluded mouse from this analysis')
    print('12. update the parameters of this analysis')
    print('13. export normalized 490 data to .mat')
    print('14. exit')
    print('')
    ans=input('(input the number of the desired task): ')



    tasks={
        '1':a.plot_both,
        '2':a.plot_490,
        '3':load_append_save_cli,
        '4':a.save,
        '5':ind_peak_df_f_cli,
        '6':mean_peak_df_f_cli,
        '7':bin_avg_cli,
        '8':bin_auc_cli,
        '9':bin_plot_cli,
        '10':remove_mouse_cli,
        '11':retrieve_excluded_cli,
        '12':update_params_cli,
        '13':a.export_to_mat,
        }
    
    try:
        tasks[ans]()
    except KeyError:
        running=False
