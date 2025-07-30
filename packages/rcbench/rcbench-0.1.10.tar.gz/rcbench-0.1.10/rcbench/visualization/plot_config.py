from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any
import os

class BasePlotConfig:
    """Base configuration for plotting."""
    
    def __init__(self,
                figsize: Tuple[int, int] = (10, 6),
                dpi: int = 100,
                save_dir: Optional[str] = None,
                show_plot: bool = True,
                plot_input_signal: bool = True,
                plot_output_responses: bool = True,
                plot_nonlinearity: bool = True,
                plot_frequency_analysis: bool = True,
                frequency_range: Optional[Tuple[float, float]] = None,
                nonlinearity_plot_style: str = 'scatter',
                prediction_sample_count: int = 200):
        """
        Initialize the base plot configuration.
        
        Args:
            figsize (Tuple[int, int]): Figure size (width, height)
            dpi (int): Figure resolution
            save_dir (Optional[str]): Directory to save plots to
            show_plot (bool): Whether to display plots
            plot_input_signal (bool): Whether to plot the input signal
            plot_output_responses (bool): Whether to plot node responses
            plot_nonlinearity (bool): Whether to plot nonlinearity
            plot_frequency_analysis (bool): Whether to plot frequency analysis
            frequency_range (Optional[Tuple[float, float]]): Frequency range to display (min, max)
            nonlinearity_plot_style (str): Style for nonlinearity plots ('scatter' or 'line')
            prediction_sample_count (int): Number of samples to display in prediction plots
        """
        self.figsize = figsize
        self.dpi = dpi
        self.save_dir = save_dir
        self.show_plot = show_plot
        
        # Plot types
        self.plot_input_signal = plot_input_signal
        self.plot_output_responses = plot_output_responses
        self.plot_nonlinearity = plot_nonlinearity
        self.plot_frequency_analysis = plot_frequency_analysis
        
        # Customization options
        self.frequency_range = frequency_range
        self.nonlinearity_plot_style = nonlinearity_plot_style
        self.prediction_sample_count = prediction_sample_count
    
    def get_save_path(self, filename: str) -> Optional[str]:
        """
        Get the full path to save a file if save_dir is set.
        
        Args:
            filename (str): Name of the file
            
        Returns:
            Optional[str]: Full path to save the file
        """
        if self.save_dir is None:
            return None
            
        # Create directory if it doesn't exist
        os.makedirs(self.save_dir, exist_ok=True)
        return os.path.join(self.save_dir, filename)


class MCPlotConfig(BasePlotConfig):
    """Configuration for Memory Capacity plotting."""
    
    def __init__(self,
                 figsize: Tuple[int, int] = (10, 6),
                 dpi: int = 100,
                 save_dir: Optional[str] = None,
                 show_plot: bool = True,
                 plot_mc_curve: bool = True,
                 plot_predictions: bool = True,
                 plot_total_mc: bool = True,
                 prediction_sample_count: int = 200,
                 max_delays_to_plot: int = 5,
                 plot_input_signal: bool = True,
                 plot_output_responses: bool = True,
                 plot_nonlinearity: bool = True,
                 plot_frequency_analysis: bool = True,
                 frequency_range: Optional[Tuple[float, float]] = None,
                 nonlinearity_plot_style: str = 'scatter'):
        """
        Initialize the Memory Capacity plot configuration.
        
        Args:
            figsize (Tuple[int, int]): Figure size (width, height)
            dpi (int): Figure resolution
            save_dir (Optional[str]): Directory to save plots to
            show_plot (bool): Whether to display plots
            plot_mc_curve (bool): Whether to plot the memory capacity curve
            plot_predictions (bool): Whether to plot predictions for each delay
            plot_total_mc (bool): Whether to plot total memory capacity
            prediction_sample_count (int): Number of samples to show in prediction plots
            max_delays_to_plot (int): Maximum number of delays to plot predictions for
            plot_input_signal (bool): Whether to plot the input signal
            plot_output_responses (bool): Whether to plot node responses
            plot_nonlinearity (bool): Whether to plot nonlinearity
            plot_frequency_analysis (bool): Whether to plot frequency analysis
            frequency_range (Optional[Tuple[float, float]]): Frequency range to display (min, max)
            nonlinearity_plot_style (str): Style for nonlinearity plots ('scatter' or 'line')
        """
        super().__init__(
            figsize=figsize,
            dpi=dpi,
            save_dir=save_dir,
            show_plot=show_plot,
            plot_input_signal=plot_input_signal,
            plot_output_responses=plot_output_responses,
            plot_nonlinearity=plot_nonlinearity,
            plot_frequency_analysis=plot_frequency_analysis,
            frequency_range=frequency_range,
            nonlinearity_plot_style=nonlinearity_plot_style,
            prediction_sample_count=prediction_sample_count
        )
        
        # MC-specific options
        self.plot_mc_curve = plot_mc_curve
        self.plot_predictions = plot_predictions
        self.plot_total_mc = plot_total_mc
        self.max_delays_to_plot = max_delays_to_plot


class NLTPlotConfig(BasePlotConfig):
    """Configuration for Non-Linear Transformation plotting."""
    
    def __init__(self,
                 figsize: Tuple[int, int] = (10, 6),
                 dpi: int = 100,
                 save_dir: Optional[str] = None,
                 show_plot: bool = True,
                 plot_input_signal: bool = True,
                 plot_output_responses: bool = True,
                 plot_nonlinearity: bool = True,
                 plot_frequency_analysis: bool = True,
                 plot_target_prediction: bool = True,
                 frequency_range: Optional[Tuple[float, float]] = None,
                 nonlinearity_plot_style: str = 'scatter',
                 prediction_sample_count: int = 200):
        """
        Initialize the Non-Linear Transformation plot configuration.
        
        Args:
            figsize (Tuple[int, int]): Figure size (width, height)
            dpi (int): Figure resolution
            save_dir (Optional[str]): Directory to save plots to
            show_plot (bool): Whether to display plots
            plot_input_signal (bool): Whether to plot the input signal
            plot_output_responses (bool): Whether to plot node responses
            plot_nonlinearity (bool): Whether to plot nonlinearity
            plot_frequency_analysis (bool): Whether to plot frequency analysis
            plot_target_prediction (bool): Whether to plot target vs prediction results
            frequency_range (Optional[Tuple[float, float]]): Frequency range to display (min, max)
            nonlinearity_plot_style (str): Style for nonlinearity plots ('scatter' or 'line')
            prediction_sample_count (int): Number of samples to show in prediction plots
        """
        super().__init__(
            figsize=figsize,
            dpi=dpi,
            save_dir=save_dir,
            show_plot=show_plot,
            plot_input_signal=plot_input_signal,
            plot_output_responses=plot_output_responses,
            plot_nonlinearity=plot_nonlinearity,
            plot_frequency_analysis=plot_frequency_analysis,
            frequency_range=frequency_range,
            nonlinearity_plot_style=nonlinearity_plot_style,
            prediction_sample_count=prediction_sample_count
        )
        
        # NLT-specific options
        self.plot_target_prediction = plot_target_prediction


class SinxPlotConfig(BasePlotConfig):
    """Configuration for Sin(x) task plotting."""
    
    def __init__(self,
                 figsize: Tuple[int, int] = (10, 6),
                 dpi: int = 100,
                 save_dir: Optional[str] = None,
                 show_plot: bool = True,
                 plot_input_signal: bool = True,
                 plot_output_responses: bool = True,
                 plot_nonlinearity: bool = True,
                 plot_frequency_analysis: bool = True,
                 plot_target_prediction: bool = True,
                 frequency_range: Optional[Tuple[float, float]] = None,
                 nonlinearity_plot_style: str = 'scatter',
                 prediction_sample_count: int = 200):
        """
        Initialize the Sin(x) task plot configuration.
        
        Args:
            figsize (Tuple[int, int]): Figure size (width, height)
            dpi (int): Figure resolution
            save_dir (Optional[str]): Directory to save plots to
            show_plot (bool): Whether to display plots
            plot_input_signal (bool): Whether to plot the input signal
            plot_output_responses (bool): Whether to plot node responses
            plot_nonlinearity (bool): Whether to plot nonlinearity
            plot_frequency_analysis (bool): Whether to plot frequency analysis
            plot_target_prediction (bool): Whether to plot target vs prediction results
            frequency_range (Optional[Tuple[float, float]]): Frequency range to display (min, max)
            nonlinearity_plot_style (str): Style for nonlinearity plots ('scatter' or 'line')
            prediction_sample_count (int): Number of samples to show in prediction plots
        """
        super().__init__(
            figsize=figsize,
            dpi=dpi,
            save_dir=save_dir,
            show_plot=show_plot,
            plot_input_signal=plot_input_signal,
            plot_output_responses=plot_output_responses,
            plot_nonlinearity=plot_nonlinearity,
            plot_frequency_analysis=plot_frequency_analysis,
            frequency_range=frequency_range,
            nonlinearity_plot_style=nonlinearity_plot_style,
            prediction_sample_count=prediction_sample_count
        )
        
        # Sin(x) task specific options
        self.plot_target_prediction = plot_target_prediction


class NarmaPlotConfig(BasePlotConfig):
    """Configuration for NARMA task plotting."""
    
    def __init__(self,
                 figsize: Tuple[int, int] = (10, 6),
                 dpi: int = 100,
                 save_dir: Optional[str] = None,
                 show_plot: bool = True,
                 plot_input_signal: bool = True,
                 plot_output_responses: bool = True,
                 plot_nonlinearity: bool = True,
                 plot_frequency_analysis: bool = True,
                 plot_target_prediction: bool = True,
                 frequency_range: Optional[Tuple[float, float]] = None,
                 nonlinearity_plot_style: str = 'scatter',
                 prediction_sample_count: int = 200):
        """
        Initialize the NARMA task plot configuration.
        
        Args:
            figsize (Tuple[int, int]): Figure size (width, height)
            dpi (int): Figure resolution
            save_dir (Optional[str]): Directory to save plots to
            show_plot (bool): Whether to display plots
            plot_input_signal (bool): Whether to plot the input signal
            plot_output_responses (bool): Whether to plot node responses
            plot_nonlinearity (bool): Whether to plot nonlinearity
            plot_frequency_analysis (bool): Whether to plot frequency analysis
            plot_target_prediction (bool): Whether to plot target vs prediction results
            frequency_range (Optional[Tuple[float, float]]): Frequency range to display (min, max)
            nonlinearity_plot_style (str): Style for nonlinearity plots ('scatter' or 'line')
            prediction_sample_count (int): Number of samples to show in prediction plots
        """
        super().__init__(
            figsize=figsize,
            dpi=dpi,
            save_dir=save_dir,
            show_plot=show_plot,
            plot_input_signal=plot_input_signal,
            plot_output_responses=plot_output_responses,
            plot_nonlinearity=plot_nonlinearity,
            plot_frequency_analysis=plot_frequency_analysis,
            frequency_range=frequency_range,
            nonlinearity_plot_style=nonlinearity_plot_style,
            prediction_sample_count=prediction_sample_count
        )
        
        # NARMA task specific options
        self.plot_target_prediction = plot_target_prediction


@dataclass
class KernelPlotConfig(BasePlotConfig):
    """Configuration for Kernel Rank visualization plots."""
    plot_feature_space: bool = True
    plot_singular_values: bool = True
    plot_kernel_heatmap: bool = True
    
    # Kernel-specific settings
    max_dimensions: int = 20
    kernel_type: str = 'rbf'
    n_components: int = 3

# Factory function to create appropriate config based on measurement type
def create_plot_config(plot_type: str, **kwargs) -> BasePlotConfig:
    """
    Create a plot configuration object based on the requested type.
    
    Args:
        plot_type: Type of plot configuration ("mc", "nlt", "kernel", "sinx", "narma")
        **kwargs: Configuration parameters to override defaults
        
    Returns:
        Appropriate plot configuration object
    
    Raises:
        ValueError: If plot_type is not recognized
    """
    if plot_type.lower() == "mc":
        return MCPlotConfig(**kwargs)
    elif plot_type.lower() == "nlt":
        return NLTPlotConfig(**kwargs)
    elif plot_type.lower() == "kernel":
        return KernelPlotConfig(**kwargs)
    elif plot_type.lower() == "sinx":
        return SinxPlotConfig(**kwargs)
    elif plot_type.lower() == "narma":
        return NarmaPlotConfig(**kwargs)
    else:
        raise ValueError(f"Unknown plot type: {plot_type}") 