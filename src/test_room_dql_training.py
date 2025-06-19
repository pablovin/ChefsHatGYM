import os
import asyncio
import ast
import pandas as pd
import matplotlib.pyplot as plt
from agents.random_agent import RandomAgent
from agents.agent_dqn import AgentDQN
from rooms.room import Room


def run_room(training: bool, model_path: str, matches: int, output_folder: str):
    room = Room(
        run_remote_room=False,
        room_name="Room_DQL_Test",
        max_matches=matches,
        output_folder=output_folder,
        save_game_dataset=True,
        save_logs_game=False,
        save_logs_room=False,
    )

    agents = [
        RandomAgent(name=f"Random{i}", log_directory=room.room_dir, verbose_log=False)
        for i in range(3)
    ]
    for a in agents:
        room.connect_player(a)

    agent = AgentDQN(
        "DQL",
        training=training,
        log_directory=room.room_dir,
        verbose_console=False,
        model_path=model_path,
        load_model=not training,
    )
    room.connect_player(agent)
    asyncio.run(room.run())
    return room, agent


def plot_score_distribution(dataset_path: str, output_path: str):
    df = pd.read_csv(dataset_path, index_col=0)
    df = df[df["Action_Type"] == "END_MATCH"]
    names = ast.literal_eval(df.iloc[0]["Match_Score"])
    scores = df["Game_Score"].apply(ast.literal_eval).tolist()
    scores_arr = pd.DataFrame(scores, columns=names)
    plt.figure()
    for n in names:
        plt.plot(scores_arr[n], label=n)
    plt.xlabel("Match")
    plt.ylabel("Score")
    plt.title("Score Progression")
    plt.legend()
    plt.savefig(output_path)
    plt.close()


if __name__ == "__main__":
    model_file = os.path.join("outputs", "dql_model.h5")
    train_room, train_agent = run_room(True, model_file, 100, "outputs")
    train_agent.plot_loss(os.path.join(train_room.room_dir, "training_loss.png"))
    train_agent.plot_positions(
        os.path.join(train_room.room_dir, "training_positions.png")
    )

    test_room, test_agent = run_room(False, model_file, 100, "outputs_test")
    dataset_file = os.path.join(test_room.room_dir, "dataset", "game_dataset.pkl.csv")
    plot_score_distribution(
        dataset_file, os.path.join(test_room.room_dir, "score_progression.png")
    )
