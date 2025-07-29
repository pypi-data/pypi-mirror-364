from typing import List, Optional, Tuple
import os
import shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import (
    log_loss,
    accuracy_score,
    precision_score,
    matthews_corrcoef,
    roc_auc_score,
    confusion_matrix,
    average_precision_score,
    mean_squared_error,
    mean_absolute_error,
    r2_score,
    explained_variance_score,
    max_error,
    mean_squared_log_error,
    classification_report,
    precision_recall_curve,
    roc_curve,
    auc,
)
from sklearn.calibration import calibration_curve
import seaborn as sns
from io import BytesIO
import base64
from .custom_metrics import lift, recall_score, f1_score


class MetricsReport:
    """Class for generating reports on the metrics of a machine learning model.

    Args:
        y_true (List[int]): A list of true target values.
        y_pred (List[float]): A list of predicted target values.
        threshold (float, optional): Threshold for generating binary classification metrics. Defaults to 0.5.
        verbose (int, optional): Verbosity level. Defaults to 0.

    Attributes:
        task_type (str): Type of task, either "classification" or "regression".
        y_true (np.ndarray): A list of true target values.
        y_pred (np.ndarray): A list of predicted target values.
        threshold (float): Threshold for generating binary classification metrics.
        metrics (dict): A dictionary containing all metrics generated.
        target_info (dict): A dictionary containing information about the target variable.
    """

    def __init__(self, y_true: List[int], y_pred: List[float], threshold: float = 0.5, verbose: int = 0):
        self.task_type = self._determine_task_type(y_true)
        self.y_true = np.array(y_true)
        self.y_pred = np.array(y_pred)
        self.threshold = threshold
        self.metrics = {}
        self.target_info = {}

        if self.task_type == "classification":
            self.y_pred_binary = (self.y_pred > self.threshold).astype(int)
            if sum(self.y_true) == 0:
                raise ValueError("For classification tasks, y_true should contain at least one True value.")
            if sum(self.y_pred_binary) == 0:
                print(f"Warning: For classification tasks threshold {self.threshold}, sum y_pred: 0, -> should contain at least one True value.")
            self.metrics = self._generate_classification_metrics()
        else:
            self.y_pred_nonnegative = np.maximum(self.y_pred, 0)
            self.metrics = self._generate_regression_metrics()

        self.binary_plots = {
            "all_count_metrics": self.plot_all_count_metrics,
            "class_hist": self.plot_class_hist,
            "tp_fp_with_optimal_threshold": self.plot_tp_fp_with_optimal_threshold,
            "class_distribution": self.plot_class_distribution,
            "confusion_matrix": self.plot_confusion_matrix,
            "precision_recall_curve": self.plot_precision_recall_curve,
            "roc_curve": self.plot_roc_curve,
            "ks_statistic": self.plot_ks_statistic,
            "calibration_curve": self.plot_calibration_curve,
            "cumulative_gain": self.plot_cumulative_gains_chart,
            "cumulative_accuracy_profile": self.plot_cap,
            "precision_recall_vs_threshold": self.plot_precision_recall_vs_threshold,
            "lift_curve": self.plot_lift_curve
        }

        self.reg_plots = {
            "residual_plot": self.plot_residual_plot,
            "predicted_vs_actual": self.plot_predicted_vs_actual
        }

    def _determine_task_type(self, y_true: List[int]) -> str:
        """Determines the type of task based on the number of unique values in y_true.

        Args:
            y_true (List[int]): A list of true target values.

        Returns:
            str: The type of task, either "classification" or "regression".
        """
        return "regression" if len(np.unique(y_true)) > 2 else "classification"

    ########## Classification Metrics ###################################################

    def _generate_classification_metrics(self) -> dict:
        """Generates a dictionary of classification metrics.

        Returns:
            dict: A dictionary of classification metrics.
        """
        cm = confusion_matrix(self.y_true, self.y_pred_binary).ravel()
        tn, fp, fn, tp = (cm if cm.size == 4 else [0, 0, 0, 0])
        report = classification_report(
            y_true=self.y_true,
            y_pred=self.y_pred_binary,
            output_dict=True,
            labels=[0, 1],
            target_names=['negative', 'positive'],
            zero_division=0
        )
        report = pd.json_normalize(report, sep=' ').to_dict(orient='records')[0]

        metrics = {
            'AP': round(average_precision_score(self.y_true, self.y_pred), 4),
            'AUC': round(roc_auc_score(self.y_true, self.y_pred), 4),
            'Log Loss': round(log_loss(self.y_true, self.y_pred), 4),
            'MSE': round(mean_squared_error(self.y_true, self.y_pred), 4),
            'Accuracy': round(accuracy_score(self.y_true, self.y_pred_binary), 4),
            'Precision_weighted': round(precision_score(self.y_true, self.y_pred_binary, average='weighted', zero_division=0), 4),
            'MCC': round(matthews_corrcoef(self.y_true, self.y_pred_binary), 4),
            'TN': tn,
            'FP': fp,
            'FN': fn,
            'TP': tp,
            'P precision': round(report['positive precision'], 4),
            'P recall': round(report['positive recall'], 4),
            'P f1-score': round(report['positive f1-score'], 4),
            'P support': report['positive support'],
            'N precision': round(report['negative precision'], 4),
            'N recall': round(report['negative recall'], 4),
            'N f1-score': round(report['negative f1-score'], 4),
            'N support': report['negative support']
        }
        return metrics

    ########## Plotting Functions ###################################################

    def plot_roc_curve(
        self,
        figsize: Tuple[int, int] = (15, 10),
        title: str = 'Receiver Operating Characteristic',
        curves: Tuple[str] = ('micro', 'macro'),
        title_fontsize: str = "large",
        text_fontsize: str = "medium",
        dpi: int = 75
    ) -> plt.Figure:
        """Generates the ROC curve from labels and predicted scores/probabilities for binary classification.

        Args:
            figsize (Tuple[int, int], optional): Figure size of the plot. Defaults to (15, 10).
            title (str, optional): Title of the generated plot. Defaults to 'Receiver Operating Characteristic'.
            curves (Tuple[str], optional): Listing of which curves to plot ('micro', 'macro'). Defaults to ('micro', 'macro').
            title_fontsize (str, optional): Matplotlib-style fontsizes for the title. Defaults to 'large'.
            text_fontsize (str, optional): Matplotlib-style fontsizes for the text. Defaults to 'medium'.
            dpi (int, optional): Dots per inch for the plot. Defaults to 75.

        Returns:
            plt.Figure: A matplotlib figure object that can be shown or saved.
        """
        y_true = np.array(self.y_true)
        y_pred = np.array(self.y_pred)

        if not any(curve in curves for curve in ('micro', 'macro')):
            raise ValueError('curves must contain "micro" or "macro"')

        # Compute ROC curve and ROC area for binary classification
        fpr, tpr, thresholds = roc_curve(y_true, y_pred)
        roc_auc = auc(fpr, tpr)

        # Compute micro-average ROC curve and ROC area
        fpr_micro, tpr_micro, _ = roc_curve(y_true.ravel(), y_pred.ravel())
        roc_auc_micro = auc(fpr_micro, tpr_micro)

        # Compute macro-average ROC curve and ROC area
        all_fpr = np.unique(np.concatenate([fpr]))
        mean_tpr = np.zeros_like(all_fpr)
        mean_tpr += np.interp(all_fpr, fpr, tpr)
        fpr_macro, tpr_macro = all_fpr, mean_tpr / 1
        roc_auc_macro = auc(fpr_macro, tpr_macro)

        # Calculate optimal threshold
        youdens_j = tpr - fpr
        optimal_idx = np.argmax(youdens_j)
        optimal_threshold = thresholds[optimal_idx]

        plt.figure(figsize=figsize, dpi=dpi)
        plt.plot(fpr, tpr, color='black', lw=2, label=f'ROC curve (area = {roc_auc:0.2f})')

        if 'micro' in curves:
            plt.plot(fpr_micro, tpr_micro, label=f'micro-average ROC curve (area = {roc_auc_micro:0.2f})', color='deeppink', linestyle=':', linewidth=4)

        if 'macro' in curves:
            plt.plot(fpr_macro, tpr_macro, label=f'macro-average ROC curve (area = {roc_auc_macro:0.2f})', color='navy', linestyle=':', linewidth=4)

        plt.plot([0, 1], [0, 1], 'r--', lw=2, label='Random guess')

        # Mark the optimal threshold
        plt.scatter(fpr[optimal_idx], tpr[optimal_idx], marker='o', color='red')
        plt.axvline(fpr[optimal_idx], color='black', linestyle=':')
        plt.axhline(tpr[optimal_idx], color='black', linestyle=':')
        plt.text(fpr[optimal_idx], tpr[optimal_idx] - 0.1, f'Threshold = {optimal_threshold:.2f}', fontsize=text_fontsize, ha='center', color='black', backgroundcolor='white')

        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate', fontsize=text_fontsize)
        plt.ylabel('True Positive Rate', fontsize=text_fontsize)
        plt.title(title, fontsize=title_fontsize)
        plt.tick_params(labelsize=text_fontsize)
        plt.legend(loc='lower right', fontsize=text_fontsize)
        plt.grid(True)
        return plt

    def plot_precision_recall_curve(
        self,
        figsize: Tuple[int, int] = (15, 10),
        title: str = 'Precision and Recall Curve',
        title_fontsize: str = "large",
        text_fontsize: str = "medium",
        dpi: int = 75
    ) -> plt.Figure:
        """Generates the Precision-Recall curve from labels and predicted scores/probabilities for binary classification.

        Args:
            figsize (Tuple[int, int], optional): Figure size of the plot. Defaults to (15, 10).
            title (str, optional): Title of the generated plot. Defaults to 'Precision and Recall Curve'.
            title_fontsize (str, optional): Matplotlib-style fontsizes for the title. Defaults to 'large'.
            text_fontsize (str, optional): Matplotlib-style fontsizes for the text. Defaults to 'medium'.
            dpi (int, optional): Dots per inch for the plot. Defaults to 75.

        Returns:
            plt.Figure: A matplotlib figure object that can be shown or saved.
        """
        y_true = np.array(self.y_true)
        y_pred = np.array(self.y_pred)

        precision, recall, thresholds = precision_recall_curve(y_true, y_pred)
        average_precision = average_precision_score(y_true, y_pred)

        # Calculate optimal threshold
        f1_scores = 2 * (precision * recall) / (precision + recall)
        optimal_idx = np.argmax(f1_scores)
        optimal_threshold = thresholds[optimal_idx]

        plt.figure(figsize=figsize, dpi=dpi)
        plt.plot(recall, precision, color='black', lw=2, label=f'PR curve (area = {average_precision:0.2f})')
        plt.plot([0, 1], [average_precision, average_precision], 'r--', lw=2, label=f'Mean precision = {average_precision:0.2f}')
        
        # Plot iso-F1 curves
        f_scores = np.linspace(0.2, 0.8, num=4)
        for f_score in f_scores:
            x = np.linspace(0.01, 1)
            y = f_score * x / (2 * x - f_score)
            plt.plot(x[y >= 0], y[y >= 0], color='gray', alpha=0.2, linestyle='--')
            plt.text(0.9, y[45] + 0.02, f'f1={f_score:0.1f}', fontsize=text_fontsize, color='gray')

        # Mark the optimal threshold
        plt.scatter(recall[optimal_idx], precision[optimal_idx], marker='o', color='red')
        plt.axvline(recall[optimal_idx], color='black', linestyle=':')
        plt.axhline(precision[optimal_idx], color='black', linestyle=':')
        plt.text(recall[optimal_idx], precision[optimal_idx] - 0.1, f'Threshold = {optimal_threshold:.2f}', fontsize=text_fontsize, ha='center', color='black', backgroundcolor='white')

        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('Recall', fontsize=text_fontsize)
        plt.ylabel('Precision', fontsize=text_fontsize)
        plt.title(title, fontsize=title_fontsize)
        plt.tick_params(labelsize=text_fontsize)
        plt.legend(loc='lower left', fontsize=text_fontsize)
        plt.grid(True)
        return plt

    def plot_confusion_matrix(self, figsize: Tuple[int, int] = (15, 10), font_size: int = 12, font_weight: str = 'bold', dpi: int = 75) -> plt:
        """Generates a confusion matrix plot.

        Args:
            figsize (Tuple[int, int], optional): Figure size for the plot. Defaults to (15, 10).
            font_size (int, optional): Font size for the numbers inside the confusion matrix. Defaults to 12.
            font_weight (str, optional): Font weight for the numbers inside the confusion matrix. Defaults to 'bold'.
            dpi (int, optional): Dots per inch for the plot. Defaults to 75.

        Returns:
            plt: The matplotlib.pyplot object with the plot.
        """
        cm = confusion_matrix(self.y_true, self.y_pred_binary)
        plt.figure(figsize=figsize, dpi=dpi)
        plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
        plt.title('Confusion Matrix')
        plt.colorbar()
        tick_marks = np.arange(len(['Negative', 'Positive']))
        plt.xticks(tick_marks, ['Negative', 'Positive'], rotation=45)
        plt.yticks(tick_marks, ['Negative', 'Positive'])
        
        fmt = 'd'
        thresh = cm.max() / 2.
        for i, j in np.ndindex(cm.shape):
            plt.text(j, i, format(cm[i, j], fmt),
                     horizontalalignment="center",
                     fontsize=font_size,
                     fontweight=font_weight,
                     color="white" if cm[i, j] > thresh else "black")
        
        plt.ylabel('True label')
        plt.xlabel('Predicted label')
        plt.tight_layout()
        return plt

    def plot_class_distribution(
        self,
        threshold: Optional[float] = None,
        display_prediction: bool = True,
        alpha: float = 0.5,
        jitter: float = 0.3,
        pal_colors: Optional[List[str]] = None,
        display_violin: bool = True,
        c_violin: str = 'white',
        strip_marker_size: int = 4,
        strip_lw_edge: Optional[float] = None,
        strip_c_edge: Optional[str] = None,
        ls_thresh_line: str = ':',
        c_thresh_line: str = 'red',
        lw_thresh_line: float = 2,
        title: Optional[str] = None,
        figsize: Tuple[int, int] = (15, 10),
        dpi: int = 75
    ) -> plt:
        """Plot distribution of the predictions for each class.

        Note: Threshold here is important because it defines colors for True Positive,
        False Negative, True Negative, and False Positive.

        Args:
            threshold (Optional[float], optional): Threshold to determine the rate between positive and negative values of the classification. Defaults to self.threshold.
            display_prediction (bool, optional): Display the points representing each prediction. Defaults to True.
            alpha (float, optional): Transparency of each predicted point. Defaults to 0.5.
            jitter (float, optional): Amount of jitter (only along the categorical axis) to apply. This can be useful when you have many points and they overlap. Defaults to 0.3.
            pal_colors (Optional[List[str]], optional): Colors to use for the different levels of the hue variable. Should be something that can be interpreted by color_palette(), or a dictionary mapping hue levels to matplotlib colors. Defaults to None.
            display_violin (bool, optional): Display violin plot. Defaults to True.
            c_violin (str, optional): Color of the violin plot. Defaults to 'white'.
            strip_marker_size (int, optional): Size of markers representing predictions. Defaults to 4.
            strip_lw_edge (Optional[float], optional): Size of the linewidth for the edge of point prediction. Defaults to None.
            strip_c_edge (Optional[str], optional): Color of the linewidth for the edge of point prediction. Defaults to None.
            ls_thresh_line (str, optional): Linestyle for the threshold line. Defaults to ':'.
            c_thresh_line (str, optional): Color for the threshold line. Defaults to 'red'.
            lw_thresh_line (float, optional): Line width of the threshold line. Defaults to 2.
            title (Optional[str], optional): Title of the graphic. Defaults to None.
            figsize (Tuple[int, int], optional): Figure size for the plot. Defaults to (15, 10).
            dpi (int, optional): Dots per inch for the plot. Defaults to 75.

        Returns:
            plt: The matplotlib.pyplot object with the plot.
        """
        if pal_colors is None:
            pal_colors = ["#00C853", "#FF8A80", "#C5E1A5", "#D50000"]
        if threshold is None:
            threshold = self.threshold

        def compute_thresh(row: pd.Series, _threshold: float) -> str:
            if (row['pred'] >= _threshold) & (row['class'] == 1):
                return "TP"
            elif (row['pred'] >= _threshold) & (row['class'] == 0):
                return 'FP'
            elif (row['pred'] < _threshold) & (row['class'] == 1):
                return 'FN'
            elif (row['pred'] < _threshold) & (row['class'] == 0):
                return 'TN'

        pred_df = pd.DataFrame({'class': self.y_true, 'pred': self.y_pred})
        pred_df['type'] = pred_df.apply(lambda x: compute_thresh(x, threshold), axis=1)
        
        pred_df_plot = pred_df.copy(deep=True)
        pred_df_plot["class"] = pred_df_plot["class"].apply(lambda x: "Class 1" if x == 1 else "Class 0")
        
        plt.figure(figsize=figsize, dpi=dpi)
        
        # Plot violin prediction distribution
        if display_violin:
            sns.violinplot(x='class', y='pred', data=pred_df_plot, inner=None, color=c_violin, cut=0)

        # Plot prediction distribution
        if display_prediction:
            sns.stripplot(x='class', y='pred', hue='type', data=pred_df_plot, jitter=jitter, alpha=alpha, size=strip_marker_size, palette=sns.color_palette(pal_colors), linewidth=strip_lw_edge, edgecolor=strip_c_edge)

        # Plot threshold
        plt.axhline(y=threshold, color=c_thresh_line, linewidth=lw_thresh_line, linestyle=ls_thresh_line)
        plt.title(title if title else 'Threshold at {:.2f}'.format(threshold))

        pred_df['Predicted Class'] = pred_df['pred'].apply(lambda x: "Class 1" if x >= threshold else "Class 0")
        pred_df.columns = ['True Class', 'Predicted Proba', 'Predicted Type', 'Predicted Class']
        
        return plt

    def plot_class_hist(self, figsize: Tuple[int, int] = (15, 10), dpi: int = 75) -> plt:
        """Generates a class histogram plot, showing the distribution of predicted probabilities
        for each actual class label.

        Args:
            figsize (Tuple[int, int], optional): A tuple of the width and height of the figure. Defaults to (15, 10).
            dpi (int, optional): Dots per inch for the plot. Defaults to 75.

        Returns:
            plt: The matplotlib.pyplot object with the plot.
        """
        plt.style.use('ggplot')
        plt.figure(figsize=figsize, dpi=dpi)

        preds_for_true_0 = [pred for pred, true in zip(self.y_pred, self.y_true) if true == 0]
        preds_for_true_1 = [pred for pred, true in zip(self.y_pred, self.y_true) if true == 1]

        plt.hist(preds_for_true_0, bins=100, edgecolor='black', alpha=0.5, label='Class 0')
        plt.hist(preds_for_true_1, bins=100, edgecolor='black', alpha=0.5, label='Class 1')

        plt.axvline(x=self.threshold, color='r', linestyle='--', label=f'Threshold: {self.threshold}')

        plt.xlabel('Predicted Probability')
        plt.ylabel('Frequency')
        plt.title('Predicted Probability Histogram by Class')
        plt.legend()
        return plt

    def plot_all_count_metrics(self, step: int = 101, plot_count_coef: float = 1e-2, figsize: Tuple[int, int] = (15, 10), dpi: int = 75, fontsize: int = 10) -> plt:
        """Generates a plot of accuracy, precision, recall, and class distribution as a function of the decision threshold.

        Args:
            step (int, optional): The number of steps to take between 0 and 1. Defaults to 101.
            plot_count_coef (float, optional): The coefficient to multiply the count by in the scoring rule. Defaults to 1e-2.
            figsize (Tuple[int, int], optional): A tuple of the width and height of the figure. Defaults to (15, 10).
            dpi (int, optional): Dots per inch for the plot. Defaults to 75.
            fontsize (int, optional): Font size for the count labels. Defaults to 10.

        Returns:
            plt: The matplotlib.pyplot object with the plot.
        """
        plt.style.use('ggplot')
        plt.figure(figsize=figsize, dpi=dpi)
        accuracy_score_list = []
        precision_score_list = []
        recall_score_list = []
        list_classes = []
        list_counts = []

        pred_prob = np.array(self.y_pred)
        target = np.array(self.y_true, dtype=int)

        thresholds = np.linspace(0, 1, step)[:-1]
        for i in thresholds:
            predicted_labels = pred_prob > i

            accuracy_score_list.append(accuracy_score(target, predicted_labels))
            precision_score_list.append(precision_score(target, predicted_labels, zero_division=0))
            recall_score_list.append(recall_score(target, predicted_labels))
            list_classes.append(predicted_labels.sum() / len(predicted_labels))
            list_counts.append(predicted_labels.sum())

        plt.plot(thresholds, accuracy_score_list, label='Accuracy')
        plt.plot(thresholds, precision_score_list, label='Precision')
        plt.plot(thresholds, recall_score_list, label='Recall')
        plt.plot(thresholds, list_classes, label='Class 1 count', color='black', linestyle='--')
        plt.axvline(x=self.threshold, color='r', linestyle='--', label=f'Threshold: {self.threshold}')

        min_count, max_count = min(list_counts), max(list_counts)
        modulo_divisor = max(1, len(list_counts) // 80)
        for i, count in enumerate(list_counts):
            if count != 0 and (i % modulo_divisor == 0 or count in (min_count, max_count)) and (list_counts[i-1] / list_counts[i]) - 1 > plot_count_coef:
                y_offset = list_classes[i] + (max(list_classes) - min(list_classes)) * 0.02
                plt.text(thresholds[i], y_offset, str(count), fontsize=fontsize, rotation=90, fontweight='bold')

        plt.xlabel('Threshold')
        plt.ylabel('Scores')
        plt.title('Accuracy, Precision, Recall, and Class Distribution')
        plt.legend()
        plt.grid(True)
        return plt

    def plot_calibration_curve(self, n_bins: int = 10, figsize: Tuple[int, int] = (15, 10), dpi: int = 75) -> plt.Figure:
        """Plots calibration curves for classifier probability estimates to show how well the probabilities
        are calibrated against the actual outcomes. A perfectly calibrated model will have all points on
        the diagonal line extending from the bottom left to the top right.

        Args:
            n_bins (int, optional): The number of bins to use for the calibration curve. More bins can provide a more detailed calibration view but require more data. Defaults to 10.
            figsize (Tuple[int, int], optional): The width and height of the plot in inches. Defaults to (15, 10).
            dpi (int, optional): Dots per inch for the plot. Defaults to 75.

        Returns:
            plt.Figure: A matplotlib figure object that can be shown or saved.
        """
        plt.figure(figsize=figsize, dpi=dpi)
        plt.plot([0, 1], [0, 1], "k:", label="Perfectly calibrated")  # Ideal calibration line

        # Generate calibration curve data
        fraction_of_positives, mean_predicted_value = calibration_curve(self.y_true, self.y_pred, n_bins=n_bins)

        # Plot the calibration curve
        plt.plot(mean_predicted_value, fraction_of_positives, 's-', label='Model')
        plt.title('Calibration plots (Reliability Curves)')
        plt.xlabel('Mean predicted value')
        plt.ylabel('Fraction of positives')
        plt.ylim([-0.05, 1.05])
        plt.legend(loc='lower right')

        return plt

    def plot_lift_curve(self, figsize: Tuple[int, int] = (15, 10), dpi: int = 75) -> plt.Figure:
        """Plots the lift curve for the binary classifier to assess the effectiveness of the classifier.
        The lift curve shows how much more likely we are to capture positive responses by using the model
        compared to random guessing, across different segments of the population.

        Args:
            figsize (Tuple[int, int], optional): The width and height of the plot in inches. Defaults to (15, 10).
            dpi (int, optional): Dots per inch for the plot. Defaults to 75.

        Returns:
            plt.Figure: The matplotlib figure object for the generated lift curve plot.
        """
        if self.y_pred.ndim > 1:
            probas = self.y_pred[:, 1]  # Assuming the second column is the positive class
        else:
            probas = self.y_pred

        sorted_indices = np.argsort(probas)[::-1]
        y_sorted = self.y_true[sorted_indices]
        cumul_true = np.cumsum(y_sorted)
        sample_n = np.arange(1, len(cumul_true) + 1)
        lift = cumul_true / sample_n / np.mean(self.y_true)

        plt.figure(figsize=figsize, dpi=dpi)
        plt.plot(sample_n / len(self.y_true), lift, label='Lift Curve', drawstyle='steps-post')
        plt.plot([0, 1], [1, 1], 'k--', label='Baseline')

        plt.title('Lift Curve')
        plt.xlabel('Proportion of sample')
        plt.ylabel('Lift')
        plt.legend(loc='best')

        return plt

    def plot_ks_statistic(
        self,
        figsize: Tuple[int, int] = (15, 10),
        title: str = 'KS Statistic',
        title_fontsize: str = "large",
        text_fontsize: str = "medium",
        dpi: int = 75
    ) -> plt.Figure:
        """Generates the KS statistic plot from labels and predicted scores/probabilities for binary classification.

        Args:
            figsize (Tuple[int, int], optional): Figure size of the plot. Defaults to (15, 10).
            title (str, optional): Title of the generated plot. Defaults to 'KS Statistic'.
            title_fontsize (str, optional): Matplotlib-style fontsizes for the title. Defaults to 'large'.
            text_fontsize (str, optional): Matplotlib-style fontsizes for the text. Defaults to 'medium'.
            dpi (int, optional): Dots per inch for the plot. Defaults to 75.

        Returns:
            plt.Figure: A matplotlib figure object that can be shown or saved.
        """
        y_true = np.array(self.y_true)
        y_pred = np.array(self.y_pred)

        fpr, tpr, thresholds = roc_curve(y_true, y_pred)
        ks_statistic = tpr - fpr
        ks_max_idx = np.argmax(ks_statistic)
        ks_value = ks_statistic[ks_max_idx]
        optimal_threshold = thresholds[ks_max_idx]

        plt.figure(figsize=figsize, dpi=dpi)
        plt.plot(thresholds, tpr, color='blue', lw=2, label='TPR')
        plt.plot(thresholds, fpr, color='red', lw=2, linestyle='--', label='FPR')
        plt.plot(thresholds, ks_statistic, color='green', lw=2, label='KS Statistic')

        plt.axvline(optimal_threshold, color='black', linestyle=':')
        plt.axhline(ks_value, color='black', linestyle=':')
        plt.scatter(optimal_threshold, ks_value, marker='o', color='red')
        plt.text(optimal_threshold, ks_value, f'KS = {ks_value:.2f}\nThreshold = {optimal_threshold:.2f}', fontsize=text_fontsize, ha='center', color='black', backgroundcolor='white')

        plt.xlabel('Threshold', fontsize=text_fontsize)
        plt.ylabel('Rate', fontsize=text_fontsize)
        plt.title(title, fontsize=title_fontsize)
        plt.legend(loc='best', fontsize=text_fontsize)
        plt.grid(True)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.0])
        return plt

    def plot_precision_recall_vs_threshold(self, fp_coefficient: int = 1, figsize: Tuple[int, int] = (15, 10), dpi: int = 75) -> plt:
        """Plots Precision and Recall as a function of the decision threshold.

        Args:
            fp_coefficient (int): The coefficient to multiply FP by in the scoring rule.
            figsize (Tuple[int, int], optional): Figure size. Defaults to (15, 10).
            dpi (int, optional): Dots per inch for the plot resolution. Defaults to 75.

        Returns:
            plt: The matplotlib.pyplot object with the plot.

        Raises:
            ValueError: If y_true and probas_pred do not have the same length.
            ValueError: If y_true and probas_pred are not 1-dimensional arrays.
        """
        y_true, probas_pred = self.y_true, self.y_pred
        if len(y_true) != len(probas_pred):
            raise ValueError("y_true and probas_pred must have the same length.")
        if len(y_true.shape) != 1 or len(probas_pred.shape) != 1:
            raise ValueError("y_true and probas_pred must be 1-dimensional arrays.")
        
        thresholds_manual = np.linspace(0, 1, 100)
        TP_list, FP_list, Scores_list = [], [], []
        
        for thresh in thresholds_manual:
            pred_thresh = (probas_pred >= thresh).astype(int)
            tn, fp, fn, tp = confusion_matrix(y_true, pred_thresh).ravel()
            TP_list.append(tp)
            FP_list.append(fp)
            Scores_list.append(tp - (fp_coefficient * fp))

        optimal_idx_manual = np.argmax(Scores_list)
        optimal_threshold_manual = thresholds_manual[optimal_idx_manual]

        precision, recall, thresholds = precision_recall_curve(y_true, probas_pred)
        f1_scores = 2 * (precision * recall) / (precision + recall)
        optimal_idx = np.argmax(f1_scores)
        optimal_threshold = thresholds[optimal_idx]

        plt.figure(figsize=figsize, dpi=dpi)
        plt.plot(thresholds, precision[:-1], "b--", label="Precision")
        plt.plot(thresholds, recall[:-1], "g-", label="Recall")
        
        best_precision = precision[optimal_idx]
        best_recall = recall[optimal_idx]
        plt.scatter([optimal_threshold], [best_precision], color="blue", marker='o', label=f"Precision: {best_precision:.2f}")
        plt.scatter([optimal_threshold], [best_recall], color="green", marker='x', label=f"Recall: {best_recall:.2f}")
        plt.axvline(x=optimal_threshold, color='grey', linestyle='--', label=f'Best Threshold: {optimal_threshold:.2f}')
        
        plt.xlabel("Threshold")
        plt.ylabel("Metrics")
        plt.legend(loc="best")
        plt.title("Precision and Recall as a function of the decision threshold")
        plt.grid(True)
        
        return plt

    def plot_tp_fp_with_optimal_threshold(self, fp_coefficient: int = 1, figsize: Tuple[int, int] = (15, 10), dpi: int = 75) -> plt:
        """Plots the True Positives (TP) and False Positives (FP) rates across different thresholds and
        identifies the optimal threshold based on a scoring rule (TP - 2*FP).

        Args:
            fp_coefficient (int): The coefficient to multiply FP by in the scoring rule.
            figsize (Tuple[int, int], optional): Figure size. Defaults to (15, 10).
            dpi (int, optional): Dots per inch for the plot resolution. Defaults to 75.

        Returns:
            plt: The matplotlib.pyplot object with the plot.

        Raises:
            ValueError: If y_true and probas_pred do not have the same length.
            ValueError: If y_true and probas_pred are not 1-dimensional arrays.
        """
        y_true, probas_pred = self.y_true, self.y_pred

        if len(y_true) != len(probas_pred):
            raise ValueError("y_true and probas_pred must have the same length.")
        if len(y_true.shape) != 1 or len(probas_pred.shape) != 1:
            raise ValueError("y_true and probas_pred must be 1-dimensional arrays.")
        
        thresholds = np.linspace(0, 1, 100)
        TP_list, FP_list, Scores_list = [], [], []
        
        for thresh in thresholds:
            pred_thresh = (probas_pred >= thresh).astype(int)
            tn, fp, fn, tp = confusion_matrix(y_true, pred_thresh).ravel()
            TP_list.append(tp)
            FP_list.append(fp)
            Scores_list.append(tp - (fp_coefficient * fp))
        
        optimal_idx = np.argmax(Scores_list)
        optimal_threshold = thresholds[optimal_idx]

        plt.figure(figsize=figsize, dpi=dpi)
        plt.plot(thresholds, TP_list, "b--", label="TP (True Positives)")
        plt.plot(thresholds, FP_list, "r-", label="FP (False Positives)")
        plt.axvline(x=optimal_threshold, color='grey', linestyle='--', label=f'Optimal Threshold: {optimal_threshold:.2f}')
        plt.scatter([optimal_threshold], [TP_list[optimal_idx]], color="green", label="Optimal TP Threshold")
        plt.scatter([optimal_threshold], [FP_list[optimal_idx]], color="orange", label="Optimal FP Threshold")
        
        plt.xlabel("Threshold")
        plt.ylabel("Count")
        plt.legend(loc="best")
        plt.title("TP and FP counts as a function of the decision threshold")
        plt.grid(True)
        
        return plt

    def plot_cumulative_gains_chart(self, figsize: Tuple[int, int] = (15, 10), dpi: int = 75) -> plt:
        """Plots the Cumulative Gains Chart for a binary classifier to show how well the predicted probabilities are calibrated with the actual outcomes.

        Args:
            figsize (Tuple[int, int], optional): Figure size for the plot. Defaults to (15, 10).
            dpi (int, optional): Dots per inch for the plot resolution. Defaults to 75.

        Returns:
            plt: The matplotlib.pyplot object with the plot.
        """
        sorted_indices = np.argsort(self.y_pred)[::-1]
        sorted_y_true = self.y_true[sorted_indices]

        cumulative_gains = np.cumsum(sorted_y_true) / np.sum(sorted_y_true)
        cumulative_random = np.linspace(0, 1, len(cumulative_gains))

        plt.figure(figsize=figsize, dpi=dpi)
        plt.plot(np.linspace(0, 1, len(cumulative_gains)), cumulative_gains, label='Model')
        plt.plot(cumulative_random, cumulative_random, label='Random', linestyle='--')

        plt.xlabel('Proportion of Samples')
        plt.ylabel('Cumulative Gain')
        plt.title('Cumulative Gains Chart')
        plt.legend(loc='lower right')
        plt.grid(True)
        return plt

    def plot_cap(self, figsize: Tuple[int, int] = (15, 10), dpi: int = 75) -> plt:
        """Plots the Cumulative Accuracy Profile (CAP) for a binary classifier to visualize model performance.

        Args:
            figsize (Tuple[int, int], optional): Figure size for the plot. Defaults to (15, 10).
            dpi (int, optional): Dots per inch for the plot resolution. Defaults to 75.

        Returns:
            plt: The matplotlib.pyplot object with the plot.
        """
        sorted_indices = np.argsort(self.y_pred)[::-1]
        sorted_y_true = self.y_true[sorted_indices]

        cumulative_gains = np.cumsum(sorted_y_true)
        total_positive = np.sum(self.y_true)
        total_samples = len(self.y_true)

        cumulative_random = np.linspace(0, total_positive, total_samples)
        perfect_model = np.minimum(np.arange(1, total_samples + 1), total_positive)

        plt.figure(figsize=figsize, dpi=dpi)
        plt.plot(np.linspace(0, 1, total_samples), cumulative_gains / total_positive, label='Model')
        plt.plot(np.linspace(0, 1, total_samples), perfect_model / total_positive, label='Perfect Model', linestyle='--')
        plt.plot(np.linspace(0, 1, total_samples), cumulative_random / total_positive, label='Random Model', linestyle='--')

        plt.xlabel('Proportion of Samples')
        plt.ylabel('Cumulative Accuracy')
        plt.title('Cumulative Accuracy Profile (CAP)')
        plt.legend(loc='lower right')
        plt.grid(True)
        return plt

    ########## Regression Metrics ###################################################

    def _generate_regression_metrics(self) -> dict:
        """Generates a dictionary of regression metrics.

        Returns:
            dict: A dictionary of regression metrics.
        """
        metrics = {
            'Mean Squared Error': round(mean_squared_error(self.y_true, self.y_pred), 4),
            'Mean Squared Log Error': round(mean_squared_log_error(self.y_true, self.y_pred_nonnegative), 4),
            'Mean Absolute Error': round(mean_absolute_error(self.y_true, self.y_pred), 4),
            'R^2': round(r2_score(self.y_true, self.y_pred), 4),
            'Explained Variance Score': round(explained_variance_score(self.y_true, self.y_pred), 4),
            'Max Error': round(max_error(self.y_true, self.y_pred), 4),
            'Mean Absolute Percentage Error': round(np.mean(np.abs((self.y_true - self.y_pred) / self.y_true)) * 100, 1),
        }
        return metrics

    def plot_residual_plot(self, figsize: Tuple[int, int] = (15, 10), dpi: int = 75) -> plt:
        """Generates a residual plot.

        Args:
            figsize (Tuple[int, int], optional): Figure size for the plot. Defaults to (15, 10).
            dpi (int, optional): Dots per inch for the plot. Defaults to 75.

        Returns:
            plt: The matplotlib.pyplot object with the plot.
        """
        plt.figure(figsize=figsize, dpi=dpi)
        plt.scatter(self.y_pred, self.y_true - self.y_pred)
        plt.xlabel("Predicted Values")
        plt.ylabel("Residuals")
        plt.title("Residual Plot")
        return plt

    def plot_predicted_vs_actual(self, figsize: Tuple[int, int] = (15, 10), dpi: int = 75) -> plt:
        """Generates a predicted vs actual plot.

        Args:
            figsize (Tuple[int, int], optional): Figure size for the plot. Defaults to (15, 10).
            dpi (int, optional): Dots per inch for the plot. Defaults to 75.

        Returns:
            plt: The matplotlib.pyplot object with the plot.
        """
        plt.figure(figsize=figsize, dpi=dpi)
        plt.scatter(self.y_pred, self.y_true)
        plt.xlabel("Predicted Values")
        plt.ylabel("Actual Values")
        plt.title("Predicted vs Actual")
        return plt

    ########## HTML Report #################################################

    def __target_info(self) -> None:
        """Generates a dictionary of target information.

        Returns:
            None
        """
        if self.task_type == 'classification':
            target_info = {
                'Count of samples': self.y_true.shape[0],
                'Count True class': sum(self.y_true),
                'Count False class': (len(self.y_true) - sum(self.y_true)),
                'Class balance %': round((sum(self.y_true) / len(self.y_true)) * 100, 1),
            }
        else:
            target_info = {
                'Count of samples': self.y_true.shape[0],
                'Mean of target': round(np.mean(self.y_true), 2),
                'Std of target': round(np.std(self.y_true), 2),
                'Min of target': round(np.min(self.y_true), 2),
                'Max of target': round(np.max(self.y_true), 2),
            }
        self.target_info = target_info

    def _generate_html_report(self, folder: str = 'report_metrics', add_css: bool = True) -> str:
        """Generates an HTML report.

        Args:
            folder (str, optional): The folder to save the report in. Defaults to 'report_metrics'.
            add_css (bool, optional): Whether to add CSS styles to the report. Defaults to True.

        Returns:
            str: A string containing the HTML report.
        """
        css = """
        <style>
            body {
                font-family: Arial, sans-serif;
                font-size: 16px;
                line-height: 1.5;
                margin: 0;
                padding: 0;
                background-color: #f4f4f9;
            }
            header {
                background-color: #343a40;
                color: white;
                padding: 10px 0;
                text-align: center;
                position: fixed;
                width: 100%;
                top: 0;
                z-index: 1000;
                font-family: "Helvetica", "Arial", sans-serif;
            }
            header h1 {
                margin: 0;
                font-size: 24px;
                color: white; /* Ensure the text color is white */
                background-color: #343a40;
            }
            main {
                padding: 20px;
                margin-top: 60px;
            }
            h1, h2, h3 {
                color: #333;
            }
            table {
                width: 80%;
                margin: 20px auto;
                border-collapse: collapse;
                table-layout: fixed;
                text-align: left;
            }
            th, td {
                border: 1px solid #ccc;
                padding: 10px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            tr:hover {
                background-color: #f1f1f1;
            }
            .summary {
                background-color: #e2e8f0;
                padding: 20px;
                border-radius: 8px;
                margin: 20px auto;
                width: 80%;
            }
            .summary h2 {
                margin-top: 0;
            }
            .plot {
                text-align: center;
                margin: 20px 0;
            }
            .plot img {
                max-width: 100%;
                height: auto;
                border-radius: 15px; /* Add rounded corners */
            }
            nav {
                background-color: #333;
                color: white;
                padding: 10px;
                position: fixed;
                width: 100%;
                bottom: 0;
                text-align: center;
                z-index: 1000;
            }
            nav a {
                color: white;
                margin: 0 15px;
                text-decoration: none;
            }
            nav a:hover {
                text-decoration: underline;
            }
        </style>
        """ if add_css else ""

        html = f"""
        <!DOCTYPE html>
        <html>
            <head>
                {css}
            </head>
            <body>
                <header>
                    <h1>Metrics Report</h1>
                </header>
                <main>
                    <div class="summary">
                        <h2>Summary</h2>
                        <p>Type: {self.task_type}</p>
                        <p>Threshold: {self.threshold}</p>
                    </div>
                    <h2>Data Information</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Info</th>
                                <th>Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            {self.__generate_html_rows(self.target_info)}
                        </tbody>
                    </table>
                    <h2>Metrics</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Metric</th>
                                <th>Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            {self.__generate_html_rows(self.metrics)}
                        </tbody>
                    </table>
                    <h2>Plots</h2>
                    {self.add_webp_plots_to_html_rows()}
                </main>
            </body>
        </html>
        """
        return html

    def add_webp_plots_to_html_rows(self, figsize: Tuple[int, int] = (15, 10), dpi: int = 75) -> str:
        """Adds WebP plots to HTML rows.

        Args:
            figsize (Tuple[int, int], optional): Size of the figure for the plots. Defaults to (15, 10).
            dpi (int, optional): Dots per inch for the plot resolution. Defaults to 75.

        Returns:
            str: HTML rows with embedded WebP images.
        """
        rows = ''
        plt.ioff()
        if self.task_type == "classification":
            for name, plot_func in self.binary_plots.items():
                plot_func()
                img_buf = BytesIO()
                plt.savefig(img_buf, format='webp', bbox_inches='tight', pad_inches=0.1)
                img_buf.seek(0)
                img_base64 = base64.b64encode(img_buf.read()).decode('utf-8')
                plt.close()
                rows += f'<tr><td><img loading="lazy" src="data:image/webp;base64,{img_base64}" alt="{name}" style="border-radius: 15px;" /><br></td></tr>\n'
        elif self.task_type == "regression":
            for name, plot_func in self.reg_plots.items():
                plot_func()
                img_buf = BytesIO()
                plt.savefig(img_buf, format='webp', bbox_inches='tight', pad_inches=0.1)
                img_buf.seek(0)
                img_base64 = base64.b64encode(img_buf.read()).decode('utf-8')
                plt.close()
                rows += f'<tr><td><img loading="lazy" src="data:image/webp;base64,{img_base64}" alt="{name}" style="border-radius: 15px;" /><br></td></tr>\n'
        return rows

    def __generate_html_rows(self, data: dict) -> str:
        """Generates HTML rows.

        Args:
            data (dict): A dictionary containing the data to be displayed.

        Returns:
            str: A string containing the HTML rows.
        """
        rows = ''
        for name, value in data.items():
            rows += f'<tr><td>{name}</td><td>{value}</td></tr>\n' if isinstance(value, float) else f'<tr><td>{name}</td><td>{int(value)}</td></tr>\n'
        return rows

    def save_report(self, folder: str = 'report_metrics', name: str = 'report_metrics', verbose: int = 0) -> None:
        """Creates and saves a report in HTML format.

        Args:
            folder (str, optional): The folder to save the report to. Defaults to 'report_metrics'.
            name (str, optional): The name of the report. Defaults to 'report_metrics'.
            verbose (int, optional): Verbosity level. Defaults to 0.
        """
        if folder != '.':
            if not os.path.exists(folder):
                os.makedirs(folder)
        self.__target_info()
        html = self._generate_html_report(add_css=True)

        file_path = f'{folder}/{name}.html'
        with open(file_path, 'w') as f:
            f.write(html)

        if verbose > 0:
            print(f'Report saved in folder: {folder}')

    def print_metrics(self) -> None:
        """Prints the metrics dictionary."""
        print(pd.DataFrame(self.metrics, index=['score']).T)
        
    def _classification_plots(self, save: bool = False, folder: str = '.') -> None:
        """
        Generates a dictionary of classification plots.

        Args:
            save: A boolean indicating whether to save the plots.
            folder: The folder to save the plots in.

        Returns:
            None.
        """
        if save:
            if os.path.exists(folder+'/plots'):
                shutil.rmtree(folder+'/plots')
            os.makedirs(folder+'/plots')

        for plot_name, plot_func in self.binary_plots.items():
            plt = plot_func()
            if save:
                plt.savefig(f'{folder}/plots/{plot_name}.png')
            else:
                plt.show()
            plt.close()
            
    def _regression_plots(self, save: bool = False, folder: str = '.') -> None:
        """
        Generates a dictionary of regression plots.

        Args:
            save: Whether to save the plots to disk.
            folder: Folder path where to save the plots.
        """
        if save:
            if not os.path.exists(folder+'/plots'):
            #    shutil.rmtree(folder+'/plots')
                os.makedirs(folder+'/plots')

        for plot_name, plot_func in self.reg_plots.items():
            plt = plot_func()
            if save:
                plt.savefig(f'{folder}/plots/{plot_name}.png')
            else:
                plt.show()
            plt.close()

    def plot_metrics(self) -> None:
        """Plots classification or regression metrics based on task type."""
        if self.task_type == 'classification':
            self._classification_plots(save=False)
        elif self.task_type == 'regression':
            self._regression_plots(save=False)

    def print_report(self) -> None:
        """Prints the metrics and plots generated by MetricsReport."""
        if self.task_type == 'classification':
            print(f'Threshold = {self.threshold}')
            print("\n                  |  Classification Report | \n")
            print(classification_report(self.y_true, self.y_pred_binary, target_names=["Class 0", "Class 1"], zero_division=0))
            print("\n                  |  Metrics Report: | \n")
            self.print_metrics()
            print("\n                  |  Lift: | \n")
            print(lift(self.y_true, self.y_pred))
            print("\n                  |  Plots: | \n")
            self.plot_metrics()
        elif self.task_type == 'regression':
            print("\n                  |  Metrics Report: | \n")
            self.print_metrics()
            print("\n                  |  Plots: | \n")
            self.plot_metrics()
