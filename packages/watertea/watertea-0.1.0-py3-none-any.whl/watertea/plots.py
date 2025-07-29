import pandas as pd 
import seaborn as sns
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import matplotlib.pyplot as plt
import seaborn as sns  
sns.set_style("whitegrid")
#plt.rcParams.update({'font.size': 14})  # Set a global font size
import pandas as pd 
import seaborn as sns
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import matplotlib.pyplot as plt
import seaborn as sns  
sns.set_style("whitegrid")
#plt.rcParams.update({'font.size': 14})  # Set a global font size
import warnings
warnings.filterwarnings("ignore", category=FutureWarning) 
import numpy as np

def csv_to_models_csv():
    for l in ["c"]:
        df = pd.read_csv(l+"times.csv", header=None)
        #df.columns = ["time", "iteration","Model","Number of nodes","Checkpoint time (s)", "Async cp"]
        #df.columns = ["time", "iteration","Model","Number of nodes","Rank","Checkpoint time (s)", "Async cp","disk"]

        # adf = pd.read_csv("dtimes.csv", header=None)
        # df= pd.concat([df,adf], ignore_index=True)



        #print(df)

        #df["Rank"] = 0
        #df["disk"] = "large"
        #print(df)
        #df.reindex(columns=df.columns)
        models = ["Llama-2-7b-hf", "Llama-2-13b-hf","Llama-3.1-8B", "Llama-3.1-70B","Mixtral-8x7B-v0.1","mamba-2.8b-hf"]
        #print(adf)
        df.columns = ["time", "iteration","val_loss","Model","Number of nodes", "Rank","Checkpoint time (s)","Saving time (s)","Waiting time(s)", "Async cp","disk"]


        #df = df[df["Rank"]==0]
        #print("datasssssssssssssssssssssssssssssss")
        #print(adf)
        #print(df)
        new_df = pd.DataFrame()

        for model in models:
            subset = df [df["Model"] == model]
            q_low = subset["Checkpoint time (s)"].quantile(0.01)
            q_hi  = subset["Checkpoint time (s)"].quantile(0.99)
            subset = subset[(subset["Checkpoint time (s)"] < q_hi) & (df["Checkpoint time (s)"] > q_low)]
            new_df = pd.concat([new_df,subset],ignore_index=True)


        df = new_df

        print(df)
        final_df = pd.DataFrame()
        dfs = []
        for disk in ["large","fast"]:
            for model in models:
                for nnodes in [2,4,8,16]:
                
                    for cpt in [True, False]:
                        if (model == "Llama-2-13b-hf") & (nnodes == 16 ) & (cpt == True) & (disk == "fast"):
                            mdf = pd.DataFrame(columns = ["time", "iteration","Model","Number of nodes","Rank","Checkpoint time (s)", "Async cp","disk"])
                            mdf = pd.concat([mdf, df[(df["Model"] == model) & (df["disk"]==disk)& (df["Async cp"] == cpt )&(df["Number of nodes"] == nnodes)]])
                            mdf = mdf.drop_duplicates(subset="iteration", keep="first")
                            #mdf = mdf.groupby(["iteration","Rank"]).head(1).reset_index(drop=True)
                            mdf = mdf[:200]
                            dfs.append(mdf)
                            mdf.to_csv("data/"+l+model  + str(cpt) + disk +str(nnodes)+".csv",index =False)

################################################################################
# mylabels = ["Checkpointing", "Asynchronous checkpointing"]
# model_names = ["Llama-2-7B", "Llama-2-13B","Llama-3.1-8B", "Llama-3.1-70B"]
# custom_colors1 = {False: "#1f77b4", True: "#ff7f0e","normal_cp":"#ff7f0e"}
# custom_colors2 = {False:"#2ca02c", True: "#d62728","normal_cp":"#ff7f0e"} 
# colors = [custom_colors1,custom_colors2]
# plt.rc('axes', axisbelow=True)
# for disk, custom_colors  in zip(["large","fast"],colors):
#     plt.rcParams['axes.axisbelow'] = True
#     fig, axes = plt.subplots(ncols=2,nrows=2, figsize=(12, 10), sharey=False, dpi=600)
#     axes = axes.flatten()
#     for ax, model, model_name,alpha  in zip(axes, models,model_names,[0.5,0.6,0.7,0.9]):
#         alpha=0.75 
#         subset = df[df["Model"] == model]
#         subset = subset[subset["disk"]==disk]
#         print(model)    
#     # Calcola media e deviazione standard
#         grouped_mean = subset.groupby(['Number of nodes','Async cp'])['Checkpoint time (s)'].mean().unstack()
#         grouped_std = subset.groupby(['Number of nodes', 'Async cp'])['Checkpoint time (s)'].std().unstack()
#         grouped_count = subset.groupby(['Number of nodes','Async cp'])['Checkpoint time (s)'].count().unstack()
#     # Convert standard deviation to standard error of the mean (SEM)
#         grouped_sem = grouped_std #/ np.sqrt(grouped_count)    
#         print(grouped_count)
#         color_list = [custom_colors[col] for col in grouped_mean.columns]
#         grouped_mean.plot(kind='bar',zorder=2, ax=ax, yerr=grouped_sem, capsize=4, alpha=alpha,color=color_list, error_kw={'elinewidth':1, 'capsize':4})
#         ax.set_axisbelow(True)
#         ax.grid(True, linestyle="--", alpha=0.8,zorder=1)
#         ax.set_axisbelow(True)
#         handles, labels = ax.get_legend_handles_labels()
#         ax.set_title(f'{model_name}',fontsize=16)
#         ax.get_legend().remove()
#         plt.rc('axes', axisbelow=True)        
#         ax.set_ylabel('Avg Checkpoint Time (s)',fontsize=15)
#         ax.set_xlabel('Number of nodes',fontsize=15)
#         ax.tick_params(axis='both',labelsize=13)
#     #ax.legend(title='Async Checkpoint',loc='upper right')

#     #plt.xlabel('Number of Nodes')
#     fig.legend(handles,labels=mylabels, bbox_to_anchor=(0.82, 0.95),loc='upper center', ncol=1, fontsize=13)
#     plt.tight_layout()
#     plt.savefig(disk+"subplot_plot_with_std.pdf",dpi=600,format='pdf')
#####################################################################################


# plt.figure()
# for disk, custom_colors  in zip(["large","fast"],colors):
#     plt.rcParams['axes.axisbelow'] = True
#     #fig, axes = plt.subplots(ncols=2,nrows=2, figsize=(12, 10), sharey=True, dpi=600)
#     #axes = axes.flatten()
#     for model, model_name,alpha  in zip(models,model_names,[0.5,0.6,0.7,0.9]):
#         alpha=0.75 
#         subset = df[df["Model"] == model]
#         subset = subset[subset["disk"]==disk]
#         subset = subset[subset["Async cp"]==True]
#         print(model)    
#     # Calcola media e deviazione standard
#         grouped_mean = subset.groupby(['Number of nodes'])['Checkpoint time (s)'].mean()
#         grouped_std = subset.groupby(['Number of nodes'])['Checkpoint time (s)'].std()
#         grouped_count = subset.groupby(['Number of nodes'])['Checkpoint time (s)'].count()
#     # Convert standard deviation to standard error of the mean (SEM)
#         grouped_sem = grouped_std #/ np.sqrt(grouped_count)    
# #        print(grouped_mean.columns)
#         #color_list = [custom_colors[col] for col in grouped_mean.columns]
#         #grouped_mean.plot(kind="scatter", zorder=2, ax=ax, yerr=grouped_sem, capsize=4, alpha=alpha,color=color_list, error_kw={'elinewidth':1, 'capsize':4})
#         plt.plot(grouped_mean,label=model)
#         #ax.set_axisbelow(True)
#         #ax.grid(True, linestyle="--", alpha=0.8,zorder=1)
#         #ax.set_axisbelow(True)
#         handles, labels = ax.get_legend_handles_labels()
#         #ax.set_title(f'{model_name}',fontsize=16)
#         #ax.get_legend().remove()
#         plt.rc('axes', axisbelow=True)        
#         #ax.set_ylabel('Avg Checkpoint Time (s)',fontsize=15)
#         #ax.set_xlabel('Number of nodes',fontsize=15)
#         #ax.tick_params(axis='both',labelsize=13)
#     #ax.legend(title='Async Checkpoint',loc='upper right')

#     #plt.xlabel('Number of Nodes')
#     fig.legend(handles,labels=mylabels, bbox_to_anchor=(0.82, 0.95),loc='upper center', ncol=1, fontsize=13)
#     plt.tight_layout()
#     plt.savefig(disk+"plotssss.pdf",dpi=600,format='pdf')


# custom_colors1 = {"large": "#1f77b4", "fast": "#2ca02c"}
# custom_colors2 = {"large":"#ff7f0e", "fast": "#d62728"} 

# colors = [custom_colors1,custom_colors2]

# mylabels=["Hard Drive","Solid State"]

# for async_cp, custom_colors  in zip([False,True],colors):
#     fig, axes = plt.subplots(ncols=2,nrows=2, figsize=(12, 10), sharey=True, dpi=600)
#     axes = axes.flatten()
#     for ax, model, model_name,alpha  in zip(axes, models,model_names,[0.5,0.6,0.7,0.9]):
#         alpha=0.75 
#         subset = df[df["Model"] == model]
#         subset = subset[subset["Async cp"]==async_cp]
#         print(model)    
#     # Calcola media e deviazione standard
#         grouped_mean = subset.groupby(['Number of nodes','disk'])['Checkpoint time (s)'].mean().unstack()
#         grouped_std = subset.groupby(['Number of nodes', 'disk'])['Checkpoint time (s)'].std().unstack()
#         grouped_count = subset.groupby(['Number of nodes','disk'])['Checkpoint time (s)'].count().unstack()
#     # Convert standard deviation to standard error of the mean (SEM)
#         grouped_mean = grouped_mean.iloc[:, ::-1]
#         grouped_std = grouped_std.iloc[:,::-1]
#         grouped_sem = grouped_std #/ np.sqrt(grouped_count)    
#         print(grouped_count)
#         color_list = [custom_colors[col] for col in grouped_mean.columns]
#         grouped_mean.plot(kind='bar', ax=ax, yerr=grouped_sem, capsize=4, alpha=alpha,color=color_list, error_kw={'elinewidth':1, 'capsize':4})
#         ax.set_axisbelow(True)
#         ax.grid(True, linestyle="--", alpha=0.8)
#         handles, labels = ax.get_legend_handles_labels()
#         ax.set_title(f'{model_name}',fontsize=16)
#         ax.get_legend().remove()
        
#         ax.set_ylabel('Avg Checkpoint Time (s)',fontsize=15)
#         ax.set_xlabel('Number of nodes',fontsize=15)
#         ax.tick_params(axis='both',labelsize=13)
#     #ax.legend(title='Async Checkpoint',loc='upper right')

#     #plt.xlabel('Number of Nodes')
#     fig.legend(handles,labels=mylabels, bbox_to_anchor=(0.82, 0.95),loc='upper center', ncol=1, fontsize=13)
#     plt.tight_layout()
#     plt.savefig(str(async_cp)+"diff.pdf",dpi=600,format='pdf')





#for ax, model in zip(axes, models):
#    subset = df[df["Model"] == model]
    
    # Calcola media e deviazione standard
#    grouped_mean = subset.groupby(['time','iteration', 'Async cp'])['Checkpoint time (s)'].mean().unstack()
#    grouped_std = subset.groupby(['time','iteration', 'Async cp'])['Checkpoint time (s)'].std().unstack()
#    grouped_count = subset.groupby(['time','iteration','Async cp'])['Checkpoint time (s)'].count().unstack()
    # Convert standard deviation to standard error of the mean (SEM)
#    grouped_sem = grouped_std #/ np.sqrt(grouped_count)    
#    print(grouped_count)
#    grouped_mean.plot(kind='bar', ax=ax, yerr=grouped_sem, capsize=4, alpha=0.75, error_kw={'elinewidth':1, 'capsize':4})

#    ax.set_title(f'{model}')
#    ax.set_ylabel('Avg Checkpoint Time (s)')
    #ax.legend(title='Async Checkpoint',loc='upper right')

#plt.xlabel('Number of Nodes')
#plt.tight_layout()
#plt.savefig("gpudiff.png")


#fig, axes = plt.subplots(ncols=len(models), figsize=(16, 6), sharey=True)
#
#df["Rank"] = df["Rank"]%4

#for ax, model in zip(axes, models):
#    subset = df[df["Model"] == model]
    
    # Calcola media e deviazione standard
#    grouped_mean = subset.groupby(['Rank', 'Async cp'])['Checkpoint time (s)'].mean().unstack()
#    grouped_std = subset.groupby(['Rank', 'Async cp'])['Checkpoint time (s)'].std().unstack()
#    grouped_count = subset.groupby(['Rank', 'Async cp'])['Checkpoint time (s)'].count().unstack()
#    # Convert standard deviation to standard error of the mean (SEM)
#    grouped_sem = grouped_std #/ np.sqrt(grouped_count)    
#    print(grouped_count)
#    grouped_mean.plot(kind='bar', ax=ax, yerr=grouped_sem, capsize=4, alpha=0.75, error_kw={'elinewidth':1, 'capsize':4})

#    ax.set_title(f'{model}')
#    ax.set_ylabel('Avg Checkpoint Time (s)')
    #ax.legend(title='Async Checkpoint',loc='upper right')

#plt.xlabel("Rank")
#plt.ylabel("Checkpoint time (s)")
#plt.title("Checkpoint Times by Rank")
#plt.legend()
#plt.grid(True)
#plt.savefig("times_gpus.png")


def histos_from_files():
    import os
    
    final_df = pd.DataFrame(columns = ["time", "iteration","val_loss","Model","Number of nodes", "Rank","Checkpoint time (s)","Saving time (s)","Waiting time(s)", "Async cp","disk"])

    # df = df[df["Rank"] == 0]
    for dirs in os.listdir("results"):
        for files in os.listdir("results/"+dirs):
            #if "131" in files:
            df = pd.read_csv("results/"+dirs+"/"+files)
            df.columns = ["time", "iteration","val_loss","Model","Number of nodes", "Rank","Checkpoint time (s)","Saving time (s)","Waiting time(s)", "Async cp","disk"]
            #df = df.drop_duplicates(subset="iteration", keep="first")
            #df = df[df["Rank"] == 0]
                # try:
                #     del df["Unnamed: 0"]
                # except:
                #    pass
                #if len(df)>10:
                    
            print(files, len(df))
            final_df = pd.concat([final_df,df])
                    #print(final_df)

    df = final_df

    mylabels = ["Checkpointing", "Asynchronous checkpointing"]
    #model_names = ["Llama-2-7b-hf", "Llama-2-13b-hf","Llama-3.1-8B", "Llama-3.1-70B","Mixtral-8x7B-v0.1","mamba-2.8b-hf"]
    
    models = pd.unique(df["Model"])
    model_names = pd.unique(df["Model"])
    custom_colors1 = {False: "#1f77b4", True: "#ff7f0e","normal_cp":"#ff7f0e"}
    custom_colors2 = {False:"#2ca02c", True: "#d62728","normal_cp":"#ff7f0e"} 
    colors = [custom_colors1,custom_colors2]
    plt.rc('axes', axisbelow=True)
    for disk, custom_colors  in zip(["large","fast"],colors):
    
        print(disk)
        plt.rcParams['axes.axisbelow'] = True
        fig, axes = plt.subplots(ncols=2,nrows=3, figsize=(12, 10), sharey=False, dpi=600)
        axes = axes.flatten()
        for ax, model, model_name,alpha  in zip(axes, models,model_names,[0.4,0.5,0.6,0.7,0.8,0.9]):
            print(model_name)
            alpha=0.75 
            subset = df[df["Model"] == model]
            subset = subset[subset["disk"]==disk]
            print(model)    
        # Calcola media e deviazione standard
            grouped_mean = subset.groupby(['Number of nodes','Async cp'])['Checkpoint time (s)'].mean().unstack()
            grouped_std = subset.groupby(['Number of nodes', 'Async cp'])['Checkpoint time (s)'].std().unstack()
            grouped_count = subset.groupby(['Number of nodes','Async cp'])['Checkpoint time (s)'].count().unstack()
        # Convert standard deviation to standard error of the mean (SEM)
            grouped_sem = grouped_std #/ np.sqrt(grouped_count)    
            print(grouped_count)
            color_list = [custom_colors[col] for col in grouped_mean.columns]
            if len(grouped_mean)>0:
                grouped_mean.plot(kind='bar',zorder=2, ax=ax, yerr=grouped_sem, capsize=4, alpha=alpha,color=color_list, error_kw={'elinewidth':1, 'capsize':4})
            ax.set_axisbelow(True)
            ax.grid(True, linestyle="--", alpha=0.8,zorder=1)
            ax.set_axisbelow(True)
            handles, labels = ax.get_legend_handles_labels()
            ax.set_title(f'{model_name}',fontsize=16)
            legend = ax.get_legend()
            if legend is not None:
                legend.remove()
            plt.rc('axes', axisbelow=True)        
            ax.set_ylabel('Avg Checkpoint Time (s)',fontsize=15)
            ax.set_xlabel('Number of nodes',fontsize=15)
            ax.tick_params(axis='both',labelsize=13)
        #ax.legend(title='Async Checkpoint',loc='upper right')
    
        #plt.xlabel('Number of Nodes')
        fig.legend(handles,labels=mylabels, bbox_to_anchor=(0.82, 0.95),loc='upper center', ncol=1, fontsize=13)
        plt.tight_layout()
        plt.savefig(disk+"subplot_plot_with_std.pdf",dpi=600,format='pdf')



def histos2_from_files():
    import os
    
    final_df = pd.DataFrame(columns = ["time", "iteration","val_loss","Model","Number of nodes", "Rank","Checkpoint time (s)","Saving time (s)","Waiting time(s)", "Async cp","disk"])

    # df = df[df["Rank"] == 0]
    for dirs in os.listdir("results"):
        for files in os.listdir("results/"+dirs):
            #if "131" in files:
            df = pd.read_csv("results/"+dirs+"/"+files)
            df.columns = ["time", "iteration","val_loss","Model","Number of nodes", "Rank","Checkpoint time (s)","Saving time (s)","Waiting time(s)", "Async cp","disk"]
            #df = df.drop_duplicates(subset="iteration", keep="first")
            #df = df[df["Rank"] == 0]
                # try:
                #     del df["Unnamed: 0"]
                # except:
                #    pass
                #if len(df)>10:
                    
            print(files, len(df))
            final_df = pd.concat([final_df,df])
                    #print(final_df)

    df = final_df
    mylabels = ["Checkpointing", "Asynchronous checkpointing"]
    #indexAge = df[df['Model'] == "mistral-7b"].index
    #df.drop(indexAge, inplace=True)
    model_names = ["Llama-2-7b-hf", "Llama-2-13b-hf","Llama-3.1-8B", "Llama-3.1-70B","Mistral-7b","Mamba-2.8b"]
    models = pd.unique(df["Model"])
    model_names = pd.unique(df["Model"])
    custom_colors1 = {False: "#1f77b4", True: "#ff7f0e","normal_cp":"#ff7f0e"}
    custom_colors2 = {False:"#2ca02c", True: "#d62728","normal_cp":"#ff7f0e"} 
    colors = [custom_colors1,custom_colors2]
    plt.rc('axes', axisbelow=True)
    #for disk, custom_colors  in zip(["large","fast"],colors):

    plt.rcParams['axes.axisbelow'] = True
    #fig, axes = plt.subplots(ncols=1,nrows=1, figsize=(15, 10), sharey=False, dpi=600)
    #df[df['Model']!= "mistral-7b"]
    #axes = axes.flatten()
    plt.figure(dpi=600)
    for model, model_name in zip(models,model_names):
        print(model_name)
        alpha=0.75 
        #subset = df[df["Model"] == model]

        subset = df[df["disk"]=="large"]
        subset = df[df["Async cp"] == True]
        print(model)    
    # Calcola media e deviazione standard
        grouped_mean = subset.groupby(['Number of nodes','Model'])['Checkpoint time (s)'].mean().unstack()
        grouped_std = subset.groupby(['Number of nodes', 'Model'])['Checkpoint time (s)'].std().unstack()
        grouped_count = subset.groupby(['Number of nodes','Model'])['Checkpoint time (s)'].count().unstack()
    # Convert standard deviation to standard error of the mean (SEM)
        grouped_sem = grouped_std #/ np.sqrt(grouped_count)    
        print(grouped_count)
        #color_list = [custom_colors[col] for col in grouped_mean.columns]
        if len(grouped_mean)>0:
            grouped_mean.plot(kind='bar',zorder=2,  yerr=grouped_sem, capsize=9,  width=0.8,alpha=alpha, error_kw={'elinewidth':1, 'capsize':4})
        #ax.set_axisbelow(True)
        #ax.grid(True, linestyle="--", alpha=0.8,zorder=1)
        #ax.set_axisbelow(True)
        #handles, labels = ax.get_legend_handles_labels()
        #ax.set_title(f'{model_name}',fontsize=16)
        #legend = ax.get_legend()
        # if legend is not None:
        #     legend.remove()
        plt.rc('axes', axisbelow=True)        
        #ax.set_ylabel('Avg Checkpoint Time (s)',fontsize=15)
        #ax.set_xlabel('Number of nodes',fontsize=15)
        #ax.tick_params(axis='both',labelsize=13)
    #ax.legend(title='Async Checkpoint',loc='upper right')
        plt.ylim(0,18)
        plt.ylabel('Avg Checkpoint Time (s)',fontsize=15)
        plt.xlabel('Number of nodes',fontsize=15)
        plt.legend(loc='upper left', ncol=2, fontsize=11)
        plt.tight_layout()
        plt.savefig("models_plot_with_std.pdf",bbox_inches="tight",dpi=600,format='pdf')



if __name__=="__main__":
    #histos_from_files()
    histos2_from_files()
