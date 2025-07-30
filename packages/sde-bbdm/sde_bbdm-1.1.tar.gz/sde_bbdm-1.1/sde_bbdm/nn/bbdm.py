import torch
from diffusion import DiffusionData
from diffusion.nn import FastSamplingDiffusionModule, LatentDiffusionModule
from typing import Optional, TypeVar, Union

Module = TypeVar('Module', bound=torch.nn.Module)
E = TypeVar('E', bound=Optional[torch.nn.Module])
D = TypeVar('D', bound=Optional[torch.nn.Module])


class BBDMModule(LatentDiffusionModule[Module, E, D], FastSamplingDiffusionModule[Module]):
    def forward_diffusion(self, data: torch.Tensor, t: Optional[torch.Tensor] = None, /, condition: Optional[torch.Tensor] = None) -> tuple[
        DiffusionData, torch.Tensor]:
        # step1 create t
        x_start = data
        batch_size = x_start.shape[0]
        t = torch.randint(1, self.time_steps, (batch_size,), device=data.device).long() if t is None else t.long()

        # step2 create noise
        noise = torch.randn_like(x_start, device=x_start.device)
        assert condition is not None, 'Condition is required for forward diffusion.'

        # calculate x_t
        m_t = t / self.time_steps
        m_t = m_t.unsqueeze(1).unsqueeze(2).unsqueeze(3) # BCWH
        delta_t = 2 * (m_t - m_t ** 2)
        xt = (1 - m_t) * x_start + m_t * condition + delta_t ** 0.5 * noise
        objective = m_t * (condition - x_start) + delta_t ** 0.5 * noise
        return DiffusionData(xt, t), objective

    def sampling_step(self, data: DiffusionData, i: int, /, *, predicted_obj: Optional[torch.Tensor] = None, return_noise: bool = False) -> Union[torch.Tensor, tuple[torch.Tensor, torch.Tensor]]:
        # fast sampling
        if self.fast_sampling:
            assert self.fast_sampling_steps is not None, "Fast sampling steps must be given."
            i = len(self.fast_sampling_steps) - i
            tau, tau_minus_one = self.fast_sampling_steps[i], self.fast_sampling_steps[i - 1]
            return self.fast_sampling_step(data, tau, tau_minus_one, return_noise=return_noise, predicted_obj=predicted_obj)

        # m_t = t/T
        t = data.t
        m_t = t / self.time_steps
        m_t = m_t.unsqueeze(1).unsqueeze(2).unsqueeze(3)

        # m_t_minus_one
        m_t_minus_one = (t-1) / self.time_steps
        m_t_minus_one = m_t_minus_one.unsqueeze(1).unsqueeze(2).unsqueeze(3)

        # delta_t and delta_t_minus_one
        delta_t = 2 * (m_t - m_t ** 2)
        delta_t_minus_one = 2 * (m_t_minus_one - m_t_minus_one ** 2)
        delta_t_by_t_minus_one = delta_t - delta_t_minus_one * ((1 - m_t) ** 2) / ((1 - m_t_minus_one) ** 2)
        tilde_delta_t = delta_t_by_t_minus_one * delta_t_minus_one / delta_t

        # c_xt, c_yt, and c_epst
        c_xt = (delta_t_minus_one / delta_t) * (1 - m_t) / (1 - m_t_minus_one) + delta_t_by_t_minus_one / delta_t * (1 - m_t_minus_one)
        c_yt = m_t_minus_one - m_t * (1 - m_t) / (1 - m_t_minus_one) * (delta_t_minus_one / delta_t)
        c_epst = (1 - m_t_minus_one) * delta_t_by_t_minus_one / delta_t

        if predicted_obj is None: 
            predicted_obj, _ = self.forward(data)
            assert predicted_obj is not None, "Predicted noise must be given."
        # predict noise

        # initialize new noise
        new_noise = torch.randn_like(data.x, device=data.x.device) if t > 1 else 0

        # sampling equation
        assert data.condition is not None, "Condition must be given."
        x_t_minus_one = c_xt * data.x + c_yt * data.condition - c_epst * predicted_obj + tilde_delta_t ** 0.5 * new_noise
        # x_t_minus_one = c_xt * data.x + c_yt * data.condition - c_epst * predicted_noise
        return (x_t_minus_one, predicted_obj) if return_noise else x_t_minus_one

    def fast_sampling_step(self, data: DiffusionData, tau: int, tau_minus_one: int, /, *, return_noise: bool = False, predicted_obj: Optional[torch.Tensor] = None) -> Union[torch.Tensor, tuple[torch.Tensor, torch.Tensor]]:
        # predict noise
        objective_recon, _ = self.forward(data)
        predicted_obj = objective_recon if predicted_obj is None else predicted_obj
        assert predicted_obj is not None, "Predicted noise must be given."
        assert data.condition is not None, "Condition must be given."

        # fast sampling
        if tau == 1:
            x_t_minus_one = data.x - predicted_obj
        else:
            # reconstruct x0
            x0_recon = data.x - predicted_obj

            # m_t
            m_tau = tau / self.time_steps
            m_tau = torch.full((data.x.shape[0],), m_tau, device=data.x.device)
            m_tau = m_tau.unsqueeze(1).unsqueeze(2).unsqueeze(3)

            # m_t_minus_one
            m_tau_minus_one = tau_minus_one / self.time_steps
            m_tau_minus_one = torch.full((data.x.shape[0],), m_tau_minus_one, device=data.x.device)
            m_tau_minus_one = m_tau_minus_one.unsqueeze(1).unsqueeze(2).unsqueeze(3)

            # var_tau and var_tau_minus_one
            var_tau = 2. * (m_tau - m_tau ** 2)
            var_tau_minus_one = 2. * (m_tau_minus_one - m_tau_minus_one ** 2)

            # sigma^2_t and sigma_t
            sigma2_t = (var_tau - var_tau_minus_one * (1. - m_tau) ** 2 / (1. - m_tau_minus_one) ** 2) * var_tau_minus_one / var_tau
            sigma_t = torch.sqrt(sigma2_t)

            # calculate x_t_minus_one
            noise = torch.randn_like(data.x)
            x_tminus_mean = (1. - m_tau_minus_one) * x0_recon + m_tau_minus_one * data.condition + torch.sqrt((var_tau_minus_one - sigma2_t) / var_tau) * (data.x - (1. - m_tau) * x0_recon - m_tau * data.condition)
            x_t_minus_one = x_tminus_mean + sigma_t * noise
        return (x_t_minus_one, predicted_obj) if return_noise else x_t_minus_one


class SDEBBDMModule(BBDMModule[Module, E, D]):
    """Special case (SDE version) of BBDM where g(t) = sqrt(2)"""
    def sampling_step(self, data: DiffusionData, i: int, /, *, predicted_obj: Optional[torch.Tensor] = None, return_noise: bool = False) -> Union[torch.Tensor, tuple[torch.Tensor, torch.Tensor]]:
        # fast sampling
        if self.fast_sampling:
            assert self.fast_sampling_steps is not None, "Fast sampling steps must be given."
            i = len(self.fast_sampling_steps) - i
            tau, tau_minus_one = self.fast_sampling_steps[i], self.fast_sampling_steps[i + 1]
            return self.fast_sampling_step(data, tau, tau_minus_one, return_noise=return_noise, predicted_obj=predicted_obj)

        # m_t = t/T
        t = data.t
        m_t = t / self.time_steps
        m_t = m_t.unsqueeze(1).unsqueeze(2).unsqueeze(3)

        # c_xt, c_yt, and c_epst, tilde_delta_t
        c_xt = 1
        c_epst = 1 / t
        c_noise = (2 / self.time_steps) ** 0.5

        # check if predicted noise has already been given
        if predicted_obj is None: 
            predicted_obj, _ = self.forward(data)
            assert predicted_obj is not None, "Predicted noise must be given."

        # initialize new noise
        new_noise = torch.randn_like(data.x, device=data.x.device) if t > 1 else 0

        # sampling equation
        assert data.condition is not None, "Condition must be given."
        x_t_minus_one = c_xt * data.x - c_epst * predicted_obj - c_noise * new_noise
        return (x_t_minus_one, predicted_obj) if return_noise else x_t_minus_one

    def fast_sampling_step(self, data: DiffusionData, tau: int, tau_minus_one: int, /, *, return_noise: bool = False, predicted_obj: Optional[torch.Tensor] = None) -> Union[torch.Tensor, tuple[torch.Tensor, torch.Tensor]]:
        # predict noise
        objective_recon, _ = self.forward(data)
        predicted_obj = objective_recon if predicted_obj is None else predicted_obj
        assert predicted_obj is not None, "Predicted noise must be given."
        assert data.condition is not None, "Condition must be given."

        # fast sampling
        if tau == 1:
            x_t_minus_one = data.x - predicted_obj
        else:
            # reconstruct x0
            x0_recon = data.x - predicted_obj

            # m_t
            m_tau = tau / self.time_steps
            m_tau = torch.full((data.x.shape[0],), m_tau, device=data.x.device)
            m_tau = m_tau.unsqueeze(1).unsqueeze(2).unsqueeze(3)

            # m_t_minus_one
            m_tau_minus_one = tau_minus_one / self.time_steps
            m_tau_minus_one = torch.full((data.x.shape[0],), m_tau_minus_one, device=data.x.device)
            m_tau_minus_one = m_tau_minus_one.unsqueeze(1).unsqueeze(2).unsqueeze(3)

            # var_tau and var_tau_minus_one
            var_tau = 2. * (m_tau - m_tau ** 2)
            var_tau_minus_one = 2. * (m_tau_minus_one - m_tau_minus_one ** 2)

            # sigma^2_t and sigma_t
            sigma_t = 0.5 * var_tau_minus_one

            # calculate x_t_minus_one
            noise = torch.randn_like(data.x)
            x_tminus_mean = (1. - m_tau_minus_one) * x0_recon + m_tau_minus_one * data.condition + torch.sqrt((var_tau_minus_one - sigma_t ** 2) / var_tau) * (data.x - (1. - m_tau) * x0_recon - m_tau * data.condition)
            x_t_minus_one = x_tminus_mean + sigma_t * noise
        return (x_t_minus_one, predicted_obj) if return_noise else x_t_minus_one
