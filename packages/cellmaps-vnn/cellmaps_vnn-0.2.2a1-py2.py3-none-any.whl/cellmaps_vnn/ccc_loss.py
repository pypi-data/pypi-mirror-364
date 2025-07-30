import torch


class CCCLoss(torch.nn.Module):
    """
    A PyTorch module for calculating the Concordance Correlation Coefficient (CCC) Loss.

    The CCC Loss is a measure used in regression tasks to evaluate the agreement
    between two variables.
    """

    def __init__(self, eps=1e-6):
        """
        Initializes the CCCLoss module.

        :param eps: A small epsilon value for numerical stability. Default is 1e-6.
        :type eps: float
        """
        super(CCCLoss, self).__init__()
        self.eps = eps

    def forward(self, y_true, y_hat):
        """
        Computes the CCC loss given true and predicted values.

        :param y_true: The true values.
        :type y_true: Tensor
        :param y_hat: The predicted values.
        :type y_hat: Tensor

        :return ccc: The calculated CCC loss.
        :rtype ccc: Tensor
        """
        y_true_mean = torch.mean(y_true)
        y_hat_mean = torch.mean(y_hat)
        y_true_var = torch.var(y_true)
        y_hat_var = torch.var(y_hat)
        y_true_std = torch.std(y_true)
        y_hat_std = torch.std(y_hat)
        vx = y_true - torch.mean(y_true)
        vy = y_hat - torch.mean(y_hat)
        pcc = torch.sum(vx * vy) / (
                torch.sqrt(torch.sum(vx ** 2) + self.eps) * torch.sqrt(torch.sum(vy ** 2) + self.eps))
        ccc = (2 * pcc * y_true_std * y_hat_std) / (y_true_var + y_hat_var + (y_hat_mean - y_true_mean) ** 2)
        ccc = 1 - ccc
        return ccc
