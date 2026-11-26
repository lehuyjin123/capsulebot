% 1. Khai báo thông số hình học (SI)
D_tip = 4.04 * 1e-3;
d_hub = 1.2 * 1e-3;
L_axial = 2.6 * 1e-3;
S_arc = 13.77 * 1e-3;
rho = 997.0;
RPM_list = [1000, 3000, 5000, 7000, 9000, 12000];

% 2. Tính toán bước chân vịt hình học
R_tip = D_tip / 2.0;
R_hub = d_hub / 2.0;
N_turns = sqrt(S_arc^2 - L_axial^2) / (2 * pi * R_tip);
Pitch = L_axial / N_turns;

% In tiêu đề bảng kết quả
fprintf('%6s | %12s | %12s | %14s | %8s | %8s\n', 'RPM', 'Thrust(mN)', 'Thrust(gf)', 'Torque(uN.m)', 'K_T', 'K_Q');
fprintf('------------------------------------------------------------------------\n'); % Đã sửa lỗi repmat ở đây

% 3. Tích phân phân tố cánh (BET)
dr_elements = 100;
r_nodes = linspace(R_hub, R_tip, dr_elements);
dr = r_nodes(2) - r_nodes(1);

for i = 1:length(RPM_list)
    rpm = RPM_list(i);
    n = rpm / 60.0;
    omega = 2 * pi * n;
    T_total = 0.0;
    Q_total = 0.0;
    
    for j = 1:length(r_nodes)
        r = r_nodes(j);
        beta = atan(Pitch / (2 * pi * r));
        V_rel = omega * r;
        alpha = beta; % Trạng thái static thrust
        
        CL = 2 * pi * sin(alpha);
        CD = 0.02 + 2 * (sin(alpha)^2);
        
        % Ước lượng chiều dài dây cung phân tố
        chord = (Pitch / L_axial) * r * (sqrt(S_arc^2 - L_axial^2) / R_tip) / dr_elements;
        if chord < 0.5*1e-3
            chord = 0.5*1e-3; 
        end
        if chord > 3.0*1e-3
            chord = 3.0*1e-3; 
        end
        
        dT = 0.5 * rho * (V_rel^2) * CL * chord * dr;
        dQ = 0.5 * rho * (V_rel^2) * CD * chord * dr * r;
        
        T_total = T_total + dT;
        Q_total = Q_total + dQ;
    end
    
    if n > 0
        KT = T_total / (rho * (n^2) * (D_tip^4));
        KQ = Q_total / (rho * (n^2) * (D_tip^5));
    else
        KT = 0; 
        KQ = 0;
    end
    
    fprintf('%6d | %12.3f | %12.4f | %14.3f | %8.5f | %8.5f\n', ...
            rpm, T_total*1e3, (T_total*1e3)/9.80665, Q_total*1e6, KT, KQ);
end