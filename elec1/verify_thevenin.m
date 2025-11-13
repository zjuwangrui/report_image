function verify_thevenin()
% 主函数：验证戴维南定理
% 1. 读取原始电路和等效电路的U-I数据
% 2. 计算每个数据点的电阻
% 3. 对U-I数据进行线性拟合
% 4. 在同一张图上绘制两条U-I特性曲线及其拟合线
% 5. 保存处理后的数据和图像

    % --- 用户输入和路径定义 ---
    fprintf('[INFO] 脚本开始运行。\n');
    date_str = input('请输入日期或标识符 (例如 "20251113"): ', 's');
    
    base_path = 'elec1/output/';
    input_path_1 = fullfile(base_path, 'data', 'raw_1.csv');
    input_path_2 = fullfile(base_path, 'data', 'raw_2.csv');
    
    output_csv_1 = fullfile(base_path, 'data', [date_str, '+output_1.csv']);
    output_csv_2 = fullfile(base_path, 'data', [date_str, '+output_2.csv']);
    output_png = fullfile(base_path, 'image', [date_str, '+output.png']);
    
    % 确保输出目录存在
    if ~exist(fileparts(output_csv_1), 'dir')
        mkdir(fileparts(output_csv_1));
    end
    if ~exist(fileparts(output_png), 'dir')
        mkdir(fileparts(output_png));
    end

    % --- 数据处理 ---
    % 处理第一个数据集（原始电路）
    [data1, fit_params1] = process_circuit_data(input_path_1, output_csv_1);
    
    % 处理第二个数据集（等效电路）
    [data2, fit_params2] = process_circuit_data(input_path_2, output_csv_2);

    % --- 绘图 ---
    fprintf('[INFO] 开始绘制U-I特性曲线...\n');
    
    hFig = figure('Name', 'Thevenin Theorem Verification', 'Position', [100, 100, 800, 600]);
    hold on;
    
    % 绘制原始数据点
    plot(data1.("I(A)"), data1.("U(V)"), 'bo', 'DisplayName', 'Raw Circuit Data', 'MarkerFaceColor', 'b');
    plot(data2.("I(A)"), data2.("U(V)"), 'rs', 'DisplayName', 'Equivalent Circuit Data', 'MarkerFaceColor', 'r');
    
    % 绘制拟合曲线
    % 生成拟合线上的点
    I_fit_1 = linspace(min(data1.("I(A)")), max(data1.("I(A)")), 100);
    U_fit_1 = polyval(fit_params1, I_fit_1);
    
    I_fit_2 = linspace(min(data2.("I(A)")), max(data2.("I(A)")), 100);
    U_fit_2 = polyval(fit_params2, I_fit_2);
    
    % 创建拟合方程字符串
    eq_str1 = sprintf('Fit (Raw): U = %.2f * I + %.2f', fit_params1(1), fit_params1(2));
    eq_str2 = sprintf('Fit (Equivalent): U = %.2f * I + %.2f', fit_params2(1), fit_params2(2));
    
    plot(I_fit_1, U_fit_1, 'b-', 'DisplayName', eq_str1, 'LineWidth', 1.5);
    plot(I_fit_2, U_fit_2, 'r--', 'DisplayName', eq_str2, 'LineWidth', 1.5);
    
    % --- 图像格式化 ---
    hold off;
    grid on;
    box on;
    title('V-I Characteristic Curve Comparison');
    xlabel('Current I (A)');
    ylabel('Voltage U (V)');
    legend('show', 'Location', 'northeast');
    
    % --- 保存图像 ---
    try
        saveas(hFig, output_png);
        fprintf('[SUCCESS] 图像已成功保存到: %s\n', output_png);
    catch ME
        fprintf('[ERROR] 保存图像失败: %s\n', ME.message);
    end
    
    fprintf('[INFO] 脚本运行结束。\n');
end

function [data_table, fit_params] = process_circuit_data(input_file, output_file)
% 读取、处理并保存单个电路的数据

    fprintf('[INFO] 正在处理文件: %s\n', input_file);
    
    % --- 检查并创建虚拟数据 ---
    if ~exist(input_file, 'file')
        fprintf('[WARNING] 输入文件 %s 不存在，将创建虚拟数据。\n', input_file);
        % order,R,U(V),I(mA)
        R_dummy = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]';
        order_dummy = (1:10)';
        % 假设 E_th = 5V, R_th = 50 ohm
        E_th = 5;
        R_th = 50;
        I_dummy_A = E_th ./ (R_th + R_dummy);
        U_dummy_V = I_dummy_A .* R_dummy;
        I_dummy_mA = I_dummy_A * 1000;
        
        data_table = table(order_dummy, R_dummy, U_dummy_V, I_dummy_mA, ...
            'VariableNames', {'order', 'R', 'U(V)', 'I(mA)'});
        writetable(data_table, input_file);
        fprintf('[INFO] 虚拟数据文件已创建: %s\n', input_file);
    else
        % --- 读取数据 ---
        opts = detectImportOptions(input_file);
        opts.VariableNamesLine = 1; % 确保第一行是表头
        opts.DataLines = 2; % 数据从第二行开始
        opts.VariableNamingRule = 'preserve'; % 保持原始列名
        data_table = readtable(input_file, opts);
        fprintf('[INFO] 文件读取成功。\n');
    end
    
    % --- 数据计算 ---
    % 将电流从 mA 转换为 A
    data_table.("I(A)") = data_table.("I(mA)") / 1000;
    
    % 计算电阻（欧姆），并保留两位小数
    data_table.("R_calculated(ohm)") = round(data_table.("U(V)") ./ data_table.("I(A)"), 2);
    
    fprintf('[INFO] 数据计算完成。\n');
    
    % --- 线性拟合 U = p1*I + p2 ---
    % U是y轴, I是x轴
    fit_params = polyfit(data_table.("I(A)"), data_table.("U(V)"), 1);
    fprintf('[INFO] 线性拟合完成。斜率 (等效内阻的负值): %.2f, 截距 (等效电动势): %.2f\n', fit_params(1), fit_params(2));
    
    % --- 保存处理后的数据 ---
    try
        writetable(data_table, output_file);
        fprintf('[SUCCESS] 处理后的数据已保存到: %s\n', output_file);
    catch ME
        fprintf('[ERROR] 保存数据文件失败: %s\n', ME.message);
    end
end