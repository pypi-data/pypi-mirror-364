import pytest
import torch

from torchmil.nn.attention.prob_smooth_attention_pool import ProbSmoothAttentionPool


def test_prob_smooth_attention_pool_invalid_covar_mode():
    """
    Test that an error is raised when an invalid covariance mode is provided.
    """
    with pytest.raises(ValueError):
        ProbSmoothAttentionPool(10, covar_mode="invalid")


@pytest.mark.parametrize(
    "batch_size, bag_size, in_dim", [(2, 10, 10), (4, 20, 20), (1, 5, 30)]
)
def test_prob_smooth_attention_pool_forward(batch_size, bag_size, in_dim):
    """
    Test the forward pass of the ProbSmoothAttentionPool module.
    """
    n_samples = 5
    pool = ProbSmoothAttentionPool(in_dim)
    X = torch.randn(batch_size, bag_size, in_dim)
    z = pool(X, n_samples=n_samples)
    assert z.shape == (batch_size, in_dim, n_samples)


@pytest.mark.parametrize("covar_mode", ["diag", "zero"])
def test_prob_smooth_attention_pool_forward_with_mask(covar_mode):
    """
    Test the forward pass of the ProbSmoothAttentionPool module with a mask.
    """
    batch_size = 2
    bag_size = 10
    in_dim = 10
    n_samples = 5
    pool = ProbSmoothAttentionPool(in_dim, covar_mode=covar_mode)
    X = torch.randn(batch_size, bag_size, in_dim)
    mask = torch.randint(0, 2, (batch_size, bag_size)).bool()
    z = pool(X, mask=mask, n_samples=n_samples)
    n_samples_expected = n_samples if covar_mode == "diag" else 1
    assert z.shape == (batch_size, in_dim, n_samples_expected)


@pytest.mark.parametrize("covar_mode", ["diag", "zero"])
def test_prob_smooth_attention_pool_forward_return_att(covar_mode):
    """
    Test the forward pass of the ProbSmoothAttentionPool module with return_att_samples=True.
    """
    batch_size = 2
    bag_size = 10
    in_dim = 10
    n_samples = 5
    pool = ProbSmoothAttentionPool(in_dim, covar_mode=covar_mode)
    X = torch.randn(batch_size, bag_size, in_dim)
    z, f = pool(X, return_att_samples=True, n_samples=n_samples)
    n_samples_expected = n_samples if covar_mode == "diag" else 1
    assert z.shape == (batch_size, in_dim, n_samples_expected)
    assert f.shape == (batch_size, bag_size, n_samples_expected)


@pytest.mark.parametrize("covar_mode", ["diag", "zero"])
def test_prob_smooth_attention_pool_forward_return_attdist(covar_mode):
    """
    Test the forward pass of the ProbSmoothAttentionPool module with return_att_dist=True.
    """
    batch_size = 2
    bag_size = 10
    in_dim = 10
    n_samples = 5
    pool = ProbSmoothAttentionPool(in_dim, covar_mode=covar_mode)
    X = torch.randn(batch_size, bag_size, in_dim)
    z, mu_f, log_diag_Sigma_f = pool(X, return_att_dist=True, n_samples=n_samples)
    n_samples_expected = n_samples if covar_mode == "diag" else 1
    assert z.shape == (batch_size, in_dim, n_samples_expected)
    assert mu_f.shape == (batch_size, bag_size, 1)
    if covar_mode == "diag":
        assert log_diag_Sigma_f.shape == (batch_size, bag_size, 1)
    else:
        assert log_diag_Sigma_f is None


@pytest.mark.parametrize("covar_mode", ["diag", "zero"])
def test_prob_smooth_attention_pool_forward_return_kl_div(covar_mode):
    """
    Test the forward pass of the ProbSmoothAttentionPool module with return_kl_div=True.
    """
    batch_size = 2
    bag_size = 10
    in_dim = 10
    n_samples = 5
    pool = ProbSmoothAttentionPool(in_dim, covar_mode=covar_mode)
    X = torch.randn(batch_size, bag_size, in_dim)
    adj = (
        torch.eye(bag_size).unsqueeze(0).repeat(batch_size, 1, 1)
    )  # Identity adjacency matrix
    z, kl_div = pool(X, adj, return_kl_div=True, n_samples=n_samples)
    n_samples_expected = n_samples if covar_mode == "diag" else 1
    assert z.shape == (batch_size, in_dim, n_samples_expected)
    assert kl_div.shape == ()


@pytest.mark.parametrize("covar_mode", ["diag", "zero"])
def test_prob_smooth_attention_pool_all_returns(covar_mode):
    """
    Test the forward pass of the ProbSmoothAttentionPool module with all return options enabled.
    """
    batch_size = 2
    bag_size = 10
    in_dim = 10
    n_samples = 5
    pool = ProbSmoothAttentionPool(in_dim, covar_mode=covar_mode)
    X = torch.randn(batch_size, bag_size, in_dim)
    adj = torch.eye(bag_size).unsqueeze(0).repeat(batch_size, 1, 1)
    z, f, kl_div = pool(
        X, adj, return_att_samples=True, return_kl_div=True, n_samples=n_samples
    )
    n_samples_expected = n_samples if covar_mode == "diag" else 1
    assert z.shape == (batch_size, in_dim, n_samples_expected)
    assert f.shape == (batch_size, bag_size, n_samples_expected)
    assert kl_div.shape == ()

    z, mu_f, log_diag_Sigma_f, kl_div = pool(
        X, adj, return_att_dist=True, return_kl_div=True, n_samples=n_samples
    )
    assert z.shape == (batch_size, in_dim, n_samples_expected)
    assert mu_f.shape == (batch_size, bag_size, 1)
    if covar_mode == "diag":
        assert log_diag_Sigma_f.shape == (batch_size, bag_size, 1)
    else:
        assert log_diag_Sigma_f is None
    assert kl_div.shape == ()
