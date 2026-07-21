% Read data
data = readmatrix('force_displacement.xlsx');
% Extract data
force = data(1:1548, 1);               % Force data
displacement = data(1:900, 2);        % Displacement data

windowSize = 5;
force = movmean(force, windowSize);

T = 16;
t_force = linspace(0, T, length(force));
t_displacement = linspace(0, T, 900);

% --- Create figure ---
fig = figure('Color', 'w');
% Remove the outer box
box off;

% Set figure dimensions
fig.Units = 'inches';
fig.Position = [1 1 6 3];


% Plotting
yyaxis left;
plot(t_force, force, 'b-', 'LineWidth', 2);
ylabel('Force (N)', 'FontSize', 14, 'Color', 'b');
set(gca, 'YColor', 'b');

yyaxis right;
plot(t_displacement, displacement, 'r-', 'LineWidth', 2);
ylabel('X\_depth (mm)', 'FontSize', 14, 'Color', 'r');
set(gca, 'YColor', 'r');

xlabel('Time (s)', 'FontSize', 14);
% Set x-axis range from 0 to 16 seconds
xlim([0 16]);

% Set x-axis tick interval to 5 seconds: 0, 5, 10, 15
xticks(0:5:16);


% Set font and style
set(gca, 'FontSize', 14, 'FontName', 'Times New Roman');
% Set axis line width to 1.5
set(gca, 'LineWidth', 1.5);
% grid on;

ax = gca;
outerpos = ax.OuterPosition;
ti = ax.TightInset;
left = outerpos(1) + ti(1);
bottom = outerpos(2) + ti(2);
ax_width = outerpos(3) - ti(1) - ti(3) - 0.01;
ax_height = outerpos(4) - ti(2) - ti(4);
ax.Position = [left bottom ax_width ax_height];

% Get the handle of the current axes
ax = gca;

% Get the limits of the left and right y-axes
yyaxis left;  yl_left = ylim;
yyaxis right; yl_right = ylim;

% Manually lock the y-axis limits to prevent interference from the fill operation
yyaxis left;  ylim(yl_left);
yyaxis right; ylim(yl_right);

% Determine the combined range for the background box
y_min = min(yl_left(1), yl_right(1));
y_max = max(yl_left(2), yl_right(2));

hold on;
fill([7.9 11.49 11.49 7.9], [y_min y_min y_max y_max], ...
[1.0 0.9 0.2], 'EdgeColor', 'none', ...
'FaceAlpha', 0.3, 'HandleVisibility', 'off');

uistack(findobj(gca,'Type','patch'),'bottom');


% --- Save the figure ---
% Set output resolution to 300 dpi and save as JPEG
print(fig, 'force_displacement_plot_X_depth', '-djpeg', '-r300');