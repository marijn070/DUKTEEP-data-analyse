import pickle

if __name__ == "__main__":
    dfs = pickle.load(open("dfs.pkl", "rb"))
    print(dfs)
