import numpy as np

from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.decomposition import PCA
from typing import Dict, Union, Optional, Any, List, Tuple
from rcbench.tasks.baseevaluator import BaseEvaluator
from rcbench.tasks.featureselector import FeatureSelector
from rcbench.logger import get_logger
from rcbench.visualization.narma_plotter import NarmaPlotter
from rcbench.visualization.plot_config import NarmaPlotConfig

logger = get_logger(__name__)

def generate_narma_target(u: Union[np.ndarray, List[float]], 
                          order: int = 10, 
                          coefficients: Dict[str, float] = {'alpha':0.4, 
                                                            'beta':0.4, 
                                                            'gamma':0.6, 
                                                            'delta':0.1},
                          ) -> np.ndarray:
    """
    Generates the NARMA target series from an input signal u using a NARMA-N formulation.
    
    The NARMA-N system is defined by:
        y[t+1] = alpha * y[t] + beta * y[t] * (sum_{i=0}^{order-1} y[t-i]) 
                 + gamma * u[t-order] * u[t] + delta

    The NARMA-2 is instead defined by:
        y[t] = alpha * y[t-1] + beta * y[t-1] * y[t-2] 
                + gamma * (u[t-1])**3 + delta
                 
    Parameters:
        u (array-like): Input signal.
        order (int): Order of the NARMA system (default is 10).
        coefficients (dict) : alpha, beta, gamma, delta definition.
    
    Returns:
        np.ndarray: The generated NARMA target series.
    """
    N = len(u)
    y = np.zeros(N)

    u = normalize_to_range(u, 0, 0.5)

    alpha = coefficients['alpha']
    beta = coefficients['beta']
    gamma = coefficients['gamma']
    delta = coefficients['delta']

    if order < 2:
        raise ValueError("Unsupported NARMA order. Choose a NARMA order greater than or equal to 2.")
    elif order == 2:
        y[:order-1]=0
        for t in range(2, N):
            y[t] = (alpha * y[t-1] + 
                    beta * y[t-1] * y[t-2] + 
                    gamma * (u[t-1])**3 + 
                    delta)
    # Initialize the first 'order' elements; here they remain zero.
    else:
        y[:order-1]=u[:order-1]
        for t in range(order, N - 1):
            
            y[t + 1] = (alpha * y[t] +
                        beta * y[t] * np.sum(y[t - order:t]) +
                        gamma * u[t - order] * u[t] +
                        delta)
    return y

def normalize_to_range(u: Union[np.ndarray, List[float]], 
                       new_min: float = 0.0, 
                       new_max: float = 0.5,
                       ) -> np.ndarray:
    u = np.asarray(u)
    u_min = np.min(u)
    u_max = np.max(u)
    # Avoid division by zero if u_max == u_min:
    if u_max == u_min:
        return np.full(u.shape, new_min)
    return (u - u_min) / (u_max - u_min) * (new_max - new_min) + new_min

class NarmaEvaluator(BaseEvaluator):
    def __init__(
        self,
        input_signal: Union[np.ndarray, List[float]],
        nodes_output: np.ndarray,
        node_names: Optional[List[str]] = None,
        order: int = 2,
        alpha: float = 0.4,
        beta: float = 0.4,
        gamma: float = 0.6,
        delta: float = 0.1,
        plot_config: Optional[NarmaPlotConfig] = None
    ) -> None:
        """
        Initializes the NARMA evaluator.

        Parameters:
            input_signal (array-like): The driving input for the NARMA system.
            nodes_output (2D array): The output of the reservoir nodes.
            node_names (List[str], optional): Names of the nodes.
            order (int): The order of the NARMA system (default is 10).
            alpha, beta, gamma, delta (float): coefficients for the NARMA equation.
            plot_config (Optional[NarmaPlotConfig]): Configuration for plotting.
        """
        # Call the parent class constructor
        super().__init__(input_signal, nodes_output, node_names)
        
        self.order: int = order
        self.coefficients: Dict[str, float] = {'alpha': alpha,
                                               'beta': beta,
                                               'gamma': gamma,
                                               'delta': delta,
                                               }
        self.targets: Dict[str, np.ndarray] = self.target_generator()
        
        # Initialize plotter with provided config
        self.plotter = NarmaPlotter(config=plot_config)
        
        # Create a time array (for plotting)
        self.time = np.arange(len(input_signal))

    def target_generator(self) -> Dict[str, np.ndarray]:
        """
        Generates the NARMA target based on the provided input signal.
        Returns a dictionary with key 'narma' mapping to the target series.
        """
        target = generate_narma_target(self.input_signal, self.order, self.coefficients)
        return {'narma': target}
    
    def set_coefficients(self,
                         alpha: float = 0.4,
                         beta: float = 0.4,
                         gamma: float = 0.6,
                         delta: float = 0.1
                         ) -> None:
        """
        Sets coefficient for the generation of a NARMA target.
        """
        
        self.coefficients['alpha'] = alpha
        self.coefficients['beta'] = beta
        self.coefficients['gamma'] = gamma
        self.coefficients['delta'] = delta
        

    def evaluate_metric(self, 
                        y_true: np.ndarray, 
                        y_pred: np.ndarray, 
                        metric: str = 'NMSE'
                        ) -> float:
        """
        Evaluates the performance using the specified metric.
        Supported metrics: 'NMSE', 'RNMSE', and 'MSE'.
        """
        if metric == 'NMSE':
            return np.mean((y_true - y_pred) ** 2) / np.var(y_true)
        elif metric == 'RNMSE':
            return np.sqrt(np.mean((y_true - y_pred) ** 2) / np.var(y_true))
        elif metric == 'MSE':
            return mean_squared_error(y_true, y_pred)
        else:
            raise ValueError("Unsupported metric: choose 'NMSE', 'RNMSE', or 'MSE'")

    def run_evaluation(self,
                       metric: str ='NMSE',
                       feature_selection_method: str ='kbest',
                       num_features: Union[int, str]='all',
                       modeltype: str = "Ridge",
                       regression_alpha: float =1.0,
                       train_ratio: float =0.8,
                       plot: bool = False,
                       ) -> Dict[str, Any]:
        """
        Runs the NARMA evaluation task. It splits the data into training and testing sets,
        performs feature selection, trains a regression model (Ridge), and returns the evaluation results.

        Parameters:
            metric (str): Performance metric to evaluate the prediction.
            feature_selection_method (str): Method to select features ('kbest' or others).
            num_features (int): Number of features (nodes) to use. If None, all nodes are used.
            regression_alpha (float): Regularization parameter for Ridge regression.
            train_ratio (float): Ratio of data to use for training.
            plot (bool): If True, a prediction plot will be generated.

        Returns:
            dict: A dictionary containing evaluation accuracy, selected features, model, predictions, and true outputs.
        """
        target_waveform = self.targets['narma']
        X = self.nodes_output
        y = target_waveform

        # Train/test split using BaseEvaluator method
        X_train, X_test, y_train, y_test = self.split_train_test(X, y, train_ratio)

        # Feature selection using BaseEvaluator method
        X_train_sel, selected_features, _ = self.feature_selection(
            X_train, y_train, feature_selection_method, num_features
        )
        if feature_selection_method == 'kbest':
            X_test_sel = X_test[:, selected_features]
        else:
            X_test_sel = self.apply_feature_selection(X_test)

        # Train regression model (Ridge)
        model = self.train_regression(X_train_sel, y_train, modeltype, regression_alpha)
        y_pred = model.predict(X_test_sel)
        accuracy = self.evaluate_metric(y_test, y_pred, metric)

        return {
            'accuracy': accuracy,
            'metric': metric,
            'selected_features': selected_features,
            'model': model,
            'y_pred': y_pred,
            'y_test': y_test,
            'train_ratio': train_ratio
        }
        
    def plot_results(self, existing_results: Optional[Dict[str, Any]] = None) -> None:
        """
        Generate plots for the NARMA task evaluation results.
        
        Args:
            existing_results (Optional[Dict[str, Any]]): Results from a previous run_evaluation call.
                                                        If None, run_evaluation will be called.
        """
        # Run evaluation if results not provided
        if existing_results is None:
            results = self.run_evaluation()
        else:
            results = existing_results
            
        # Create node outputs dictionary for visualization
        node_outputs = {}
        for i, name in enumerate(self.node_names):
            node_outputs[name] = self.nodes_output[:, i]
            
        # Get test data from results
        y_test = results['y_test']
        y_pred = results['y_pred']
        
        # Calculate starting index for test data based on train_ratio
        train_ratio = results.get('train_ratio', 0.8)
        test_start_idx = int(train_ratio * len(self.input_signal))
        
        # Create time array for test data
        test_time = self.time[test_start_idx:test_start_idx + len(y_test)]
        
        # First create general plots with the full dataset (not target-specific)
        self.plotter.plot_results(
            time=self.time,
            input_signal=self.input_signal,
            node_outputs=node_outputs,
            save_dir=None
        )
        
        # Then create prediction plots with the test data subset
        if y_test is not None and y_pred is not None:
            # Calculate the test portion of the input signal
            test_input_signal = self.input_signal[test_start_idx:test_start_idx + len(y_test)]
            
            # Create a dictionary for test node outputs
            test_node_outputs = {}
            for name, output in node_outputs.items():
                test_node_outputs[name] = output[test_start_idx:test_start_idx + len(y_test)]
            
            # Now generate the target-specific plots with properly aligned time arrays
            self.plotter.plot_results(
                time=test_time,
                input_signal=test_input_signal,
                node_outputs=test_node_outputs,
                y_true=y_test,
                y_pred=y_pred,
                target_name=f"NARMA-{self.order}",
                save_dir=None
            )
