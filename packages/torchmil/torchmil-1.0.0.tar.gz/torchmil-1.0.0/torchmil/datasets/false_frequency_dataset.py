import torch
import numpy as np
from tensordict import TensorDict


class FalseFrequencyMILDataset(torch.utils.data.Dataset):
    """
    False Frequency MIL Dataset.
    Implementation from Algorithm 3 in [Reproducibility in Multiple Instance Learning: A Case For Algorithmic Unit Tests](https://proceedings.neurips.cc/paper_files/paper/2023/hash/2bab8865fa4511e445767e3750b2b5ac-Abstract-Conference.html).
    """

    def __init__(
        self,
        D: int,
        num_bags: int,
        pos_class_prob: float = 0.5,
        train: bool = True,
        seed: int = 0,
    ) -> None:
        """
        Arguments:
            D: Dimensionality of the data.
            num_bags: Number of bags in the dataset.
            pos_class_prob: Probability of a bag being positive.
            train: Whether to create the training or test dataset.
            seed: Seed for the random number generator.
        """

        super().__init__()

        self.num_bags = num_bags
        self.pos_class_prob = pos_class_prob
        self.train = train
        self.seed = seed

        # Create the distributions
        self.pos_distr = [
            torch.distributions.Normal(2 * torch.ones(D), 0.1 * torch.ones(D)),
            torch.distributions.Normal(3 * torch.ones(D), 0.1 * torch.ones(D)),
        ]
        self.neg_distr = torch.distributions.Normal(torch.zeros(D), torch.ones(D))
        self.poisoning = torch.distributions.Normal(
            -10 * torch.ones(D), 0.1 * torch.ones(D)
        )

        np.random.seed(seed)
        self.bags_list = self._create_bags()

    def _sample_positive_bag(self):
        """
        Sample a positive bag.

        Arguments:
            mode: Mode of the dataset.

        Returns:
            bag_dict: Dictionary containing the following keys:

                - data: Data of the bag.
                - label: Label of the bag.
                - inst_labels: Instance labels of the bag.
        """
        data = []
        inst_labels = []

        # Generate positive instances
        # Get count of positive instances per distribution and sample in unique comprehension
        counts = [torch.randint(low=1, high=2, size=(1,)).item() for i in range(2)]
        pos_samples = [self.pos_distr[0].sample() for _ in range(counts[0])] + [
            self.pos_distr[1].sample() for _ in range(counts[1])
        ]
        data.extend(pos_samples)
        inst_labels.extend([torch.ones(len(pos_samples))])

        # Negative instances sampling
        num_negatives = torch.randint(low=1, high=10, size=(1,)).item()
        data.extend([self.neg_distr.sample() for _ in range(num_negatives)])
        inst_labels.extend([torch.zeros(num_negatives)])

        # Stack data
        data = torch.stack(data).view(-1, data[0].shape[-1])
        inst_labels = torch.cat([t.flatten() for t in inst_labels])

        return {"X": data, "Y": torch.tensor(1), "y_inst": inst_labels}

    def _sample_negative_bag(self):
        """
        Sample a negative bag.

        Returns:
            bag_dict: Dictionary containing the following keys:

                - data: Data of the bag.
                - label: Label of the bag.
                - inst_labels: Instance labels of the bag.
        """

        data = []
        inst_labels = []

        t = (
            torch.randint(low=35, high=45, size=(1,)).item()
            if not self.train
            else torch.randint(low=1, high=2, size=(1,)).item()
        )
        c = torch.randint(low=0, high=1, size=(1,)).item()

        data.extend([self.pos_distr[c].sample() for _ in range(t)])
        inst_labels.extend([torch.ones(t)])

        # Negative instances sampling
        num_negatives = torch.randint(low=1, high=10, size=(1,)).item()
        data.extend([self.neg_distr.sample() for _ in range(num_negatives)])
        inst_labels.extend([torch.zeros(num_negatives)])

        # Stack data
        data = torch.stack(data).view(-1, data[0].shape[-1])
        inst_labels = torch.cat([t.flatten() for t in inst_labels])

        return {"X": data, "Y": torch.tensor(0), "y_inst": inst_labels}

    def _create_bags(self):
        """Generate the bags for the dataset."""

        num_pos_bags = int(self.num_bags * self.pos_class_prob)
        num_neg_bags = self.num_bags - num_pos_bags

        bags_list = []

        for _ in range(num_pos_bags):
            bags_list.append(self._sample_positive_bag())

        for _ in range(num_neg_bags):
            bags_list.append(self._sample_negative_bag())

        return bags_list

    def __len__(self) -> int:
        """
        Returns:
            Number of bags in the dataset
        """
        return len(self.bags_list)

    def __getitem__(self, index: int) -> TensorDict:
        """
        Arguments:
            index: Index of the bag to retrieve.

        Returns:
            bag_dict: Dictionary containing the following keys:

                - X: Bag features of shape `(bag_size, feat_dim)`.
                - Y: Label of the bag.
                - y_inst: Instance labels of the bag.
        """
        if index >= len(self.bags_list):
            raise IndexError(
                f"Index {index} out of range (max: {len(self.bags_list) - 1})"
            )
        return self.bags_list[index]
