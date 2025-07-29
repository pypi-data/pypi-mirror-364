# %% [markdown]
# # Inverting Earthquake Focal Mechanism using Automatic Differentiation

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn.functional as F

# %%
from torch import nn

# %% [markdown]
# ## Build forward model to calculate polarity


# %%
class FocalMechanism(nn.Module):
    """
    get radiation pattern given focal mechanism, take-off angle and azimuth angle
    reference: Aki and Richards-2002-p.108-110
    Args:
        fm: focal mechanism, [strike, dip, rake] in degree
        takeoff: take-off angle in degree, zero points to downward, np.array
        azimuth: azimuth angle in degree, zero points to north, np.array
        type: 'P' or 'SH' or 'SV'
    """

    def __init__(self, strike=[0], dip=[0], rake=[0], scale=False, dtype=torch.float32):
        super().__init__()
        self.num_event = len(strike)
        self.strike = nn.Parameter(torch.tensor(strike, dtype=dtype).unsqueeze(-1))
        self.dip = nn.Parameter(torch.tensor(dip, dtype=dtype).unsqueeze(-1))
        self.rake = nn.Parameter(torch.tensor(rake, dtype=dtype).unsqueeze(-1))
        self.scale = scale
        if self.scale:
            self.w = nn.Parameter(torch.zeros(self.num_event, dtype=dtype).unsqueeze(-1))
            # self.w = nn.Parameter(torch.ones(self.num_event, dtype=dtype).unsqueeze(-1))

    def forward(self, takeoff, azimuth, phase):
        inc = torch.deg2rad(takeoff)
        azi = torch.deg2rad(azimuth)
        strike = torch.deg2rad(self.strike)
        dip = torch.deg2rad(self.dip)
        rake = torch.deg2rad(self.rake)

        si = torch.sin(inc)
        ci = torch.cos(inc)
        s2i = torch.sin(2 * inc)
        c2i = torch.cos(2 * inc)

        sd = torch.sin(dip)
        cd = torch.cos(dip)
        s2d = torch.sin(2 * dip)
        c2d = torch.cos(2 * dip)
        sr = torch.sin(rake)
        cr = torch.cos(rake)
        sas = torch.sin(azi - strike)
        cas = torch.cos(azi - strike)

        s2as = 2 * sas * cas
        c2as = cas**2 - sas**2

        polarity_p = (
            -cas * cd * cr * s2i
            + cr * s2as * sd * si**2
            + c2d * s2i * sas * sr
            + s2d * (ci**2 + (-1) * sas**2 * si**2) * sr
        )
        polarity_sv = (
            -c2i * cas * cd * cr
            + (1 / 2) * cr * s2as * s2i * sd
            + c2d * c2i * sas * sr
            + (-1 / 2) * s2d * s2i * (1 + sas**2) * sr
        )
        polarity = torch.stack([polarity_p, polarity_sv], dim=-1)
        # polarity_sh = (
        #     cd * ci * cr * sas
        #     + c2as * cr * sd * si
        #     + c2d * cas * ci * sr
        #     + (-1 / 2) * s2as * s2d * si * sr
        # )
        # polarity = torch.stack([polarity_p, polarity_sv, polarity_sh], dim=-1)
        polarity = torch.sum(polarity * phase, dim=(-1))
        if self.scale and self.training:
            # polarity *= (torch.abs(self.w) + 1.0)
            # polarity *= (torch.exp(-self.w) + 1.0)
            # polarity *= (F.softplus(self.w) + 1.0)
            polarity *= F.elu(self.w) + 2.0

        return polarity


# %% [markdown]
# ## Generate synthetic data


# %%
def generate_data(strike, dip, rake, num=4, takeoff_angle0=None):
    with torch.no_grad():
        model = FocalMechanism(strike=strike, dip=dip, rake=rake, scale=False)
        takeoff_angles = []
        azimuths = []
        phase_types = []
        for event in range(len(strike)):
            # takeoff_angle = torch.from_numpy(np.linspace(0, 180, num))
            if takeoff_angle0 is None:
                takeoff_angle = torch.from_numpy(np.linspace(0, 180, num)).float()
            else:
                takeoff_angle = torch.from_numpy(np.array([takeoff_angle0] * (num + 1))).float()
            azimuth = torch.from_numpy(np.linspace(0, 360, num + 1)).float()
            print(takeoff_angle.shape)
            print(azimuth.shape)
            takeoff_angle, azimuth = torch.meshgrid(takeoff_angle, azimuth, indexing="ij")
            takeoff_angle = takeoff_angle.flatten()
            azimuth = azimuth.flatten()
            phase_type = torch.zeros([len(takeoff_angle), 2], dtype=torch.float32)
            phase_type[:, 0] = 1

            takeoff_angles.append(takeoff_angle)
            azimuths.append(azimuth)
            phase_types.append(phase_type)

        takeoff_angle = torch.stack(takeoff_angles, dim=0)
        azimuth = torch.stack(azimuths, dim=0)
        phase_type = torch.stack(phase_types, dim=0)
        polarity = model(takeoff_angle, azimuth, phase=phase_type)
        polarity = torch.sign(polarity)

    data = {
        "phase_polarity": polarity,
        "phase_type": phase_type,
        "takeoff_angle": takeoff_angle,
        "azimuth": azimuth,
    }
    return data


# %%
strike = [45, 30]
dip = [90, 80]
rake = [0, 60]
data = generate_data(strike, dip, rake, num=100)  # , takeoff_angle0=45)

# %%
data["phase_polarity"].shape

# %%
data["phase_polarity"]

# %%
fig, ax = plt.subplots(1, 2, figsize=(10, 5))
for i in range(len(data["azimuth"])):
    x = torch.cos(torch.deg2rad(data["azimuth"][i])) * torch.sin(torch.deg2rad(data["takeoff_angle"][i]))
    y = torch.sin(torch.deg2rad(data["azimuth"][i])) * torch.sin(torch.deg2rad(data["takeoff_angle"][i]))
    c = data["phase_polarity"][i]
    ax[i].scatter(x, y, s=100, c=c, cmap="RdBu")
    ax[i].set_xlim(-1, 1)
    ax[i].set_ylim(-1, 1)
    ax[i].set_aspect("equal")
    ax[i].set_title(f"Ground Truth {i}")

# %%
data_dense = generate_data(strike, dip, rake, num=100)

fig, ax = plt.subplots(1, 2, figsize=(10, 5))
for i in range(len(data_dense["azimuth"])):
    x = torch.cos(torch.deg2rad(data_dense["azimuth"][i])) * torch.sin(torch.deg2rad(data_dense["takeoff_angle"][i]))
    y = torch.sin(torch.deg2rad(data_dense["azimuth"][i])) * torch.sin(torch.deg2rad(data_dense["takeoff_angle"][i]))
    c = data_dense["phase_polarity"][i]
    ax[i].scatter(x, y, s=5, c=c, cmap="RdBu")
    ax[i].set_xlim(-1, 1)
    ax[i].set_ylim(-1, 1)
    ax[i].set_aspect("equal")
    ax[i].set_title(f"Ground Truth {i}")
plt.savefig("data_dense.png")

# %% [markdown]
# ## Invert Focal Mechanism

# %%
from sklearn.svm import LinearSVC

# %%
# def nodal_to_sdr(n1, n2):
#     """
#     Convert two nodal plane normal vectors to strike-dip-rake parameters.

#     Args:
#         n1, n2: Normal vectors to the two nodal planes (numpy arrays of shape (3,))

#     Returns:
#         plane1, plane2: Tuples of (strike, dip, rake) in degrees for both planes
#     """

#     def normal_to_sdr(normal, slip):
#         """Convert a single normal vector and slip vector to strike-dip-rake"""
#         nx, ny, nz = normal
#         print(f"{nx = }, {ny = }, {nz = }")

#         # Ensure normal points upward (positive z component)
#         if nz < 0:
#             normal = -normal
#             slip = -slip
#             nx, ny, nz = normal

#         # slip = -slip
#         # normal = -normal

#         # Calculate dip angle (0-90 degrees)
#         dip = np.arccos(abs(nz))

#         # Calculate strike angle (azimuth of strike direction)
#         phi = np.arctan2(-nx, ny)
#         # phi = np.arctan2(nx, -ny)  # Adjusted to match strike convention

#         # Ensure strike is in [0, 360) degrees
#         strike = np.rad2deg(phi) % 360

#         # Calculate rake angle
#         # Strike direction vector (horizontal, pointing along strike)
#         d_strike = np.array([np.cos(phi), np.sin(phi), 0])

#         # Up-dip direction (perpendicular to both normal and strike)
#         d_updip = np.cross(d_strike, normal)

#         # Project slip vector onto fault plane and calculate rake
#         rake = np.arctan2(np.dot(d_updip, slip), np.dot(d_strike, slip))

#         # Convert to degrees and ensure rake is in [-180, 180) range
#         rake_deg = np.rad2deg(rake)
#         if rake_deg > 180:
#             rake_deg -= 360
#         elif rake_deg <= -180:
#             rake_deg += 360

#         return (strike, np.rad2deg(dip), rake_deg)

#     # For nodal plane 1: normal is n1, slip direction is n2
#     plane1 = normal_to_sdr(n1, n2)

#     # For nodal plane 2: normal is n2, slip direction is n1
#     plane2 = normal_to_sdr(n2, n1)

#     return plane1, plane2


# def nodal_to_sdr(n1, n2):
#     """
#     Calculates strike, dip, and rake for two orthogonal nodal plane vectors.

#     This function computes the orientation parameters for two possible fault planes
#     given their normal vectors. It assumes a double-couple source model where the
#     slip vector on one plane is the normal to the other.

#     Args:
#         n1 (tuple or list): The (nx, ny, nz) components of the first normal vector.
#         n2 (tuple or list): The (nx, ny, nz) components of the second normal vector.

#     Returns:
#         tuple: A tuple containing two dictionaries, one for each potential fault plane.
#                Each dictionary contains the 'strike', 'dip', and 'rake'.
#                Returns (None, None) if the input vectors are not orthogonal.

#     Conventions Used:
#     - Coordinate System: Right-handed North-East-Down (NED).
#         - x: North
#         - y: East
#         - z: Down
#     - Strike: 0-360 degrees, measured clockwise from North.
#     - Dip: 0-90 degrees.
#     - Rake: -180 to 180 degrees. Angle of slip on the fault plane, measured
#             counter-clockwise from the strike direction.
#     - Normal Vector: The normal to the fault plane is constrained to point
#       upwards (z-component <= 0) for calculation consistency.
#     """

#     # --- Normalize input vectors and check for orthogonality ---
#     n1 = np.array(n1, dtype=float)
#     n2 = np.array(n2, dtype=float)

#     if np.linalg.norm(n1) == 0 or np.linalg.norm(n2) == 0:
#         print("Error: Input vectors must have non-zero length.")
#         return None, None

#     n1 /= np.linalg.norm(n1)
#     n2 /= np.linalg.norm(n2)

#     if not np.isclose(np.dot(n1, n2), 0.0, atol=1e-4):
#         print(f"Error: Input vectors are not orthogonal. Dot product: {np.dot(n1, n2)}")
#         return None, None

#     # --- Helper function to calculate SDR for one plane ---
#     def get_sdr(n_fault, n_slip):
#         """Calculates strike, dip, and rake for a single fault plane."""

#         # Convention: Normal vector must point upwards (z <= 0).
#         # If the z-component is positive (pointing down), flip both vectors.
#         # This keeps their geometric relationship but satisfies the convention.
#         if n_fault[2] > 0:
#             n_fault = -n_fault
#             n_slip = -n_slip

#         nx, ny, nz = n_fault

#         # --- Calculate Dip ---
#         # Dip is the angle between the horizontal plane and the fault plane.
#         # It's calculated from the angle between the normal vector and the vertical axis.
#         # With nz <= 0, dip = acos(-nz).
#         dip = np.degrees(np.arccos(np.clip(-nz, -1.0, 1.0)))

#         # --- Calculate Strike ---
#         # Strike is the azimuth of the line of intersection of the fault plane
#         # and the horizontal plane.
#         # Formula is derived from the geometry of the normal's horizontal projection.
#         strike = np.degrees(np.arctan2(-nx, ny))
#         if strike < 0:
#             strike += 360

#         # --- Calculate Rake ---
#         # Handle the edge case of a perfectly horizontal fault (dip=0),
#         # where strike and rake are undefined.
#         if np.isclose(dip, 0.0):
#             return strike, dip, 0.0  # Rake is undefined, return 0 by convention

#         # Create the strike vector in the NED coordinate system.
#         strike_rad = np.radians(strike)
#         strike_vec = np.array([np.cos(strike_rad), np.sin(strike_rad), 0])

#         # The "up-dip" vector is in the fault plane, perpendicular to the strike vector,
#         # and points up the dipping plane. It is found via the cross product.
#         up_dip_vec = np.cross(n_fault, strike_vec)

#         # Rake is the angle of the slip vector (n_slip) in the coordinate system
#         # defined by the strike vector and the up-dip vector.
#         # We use atan2 for a robust calculation that correctly finds the angle
#         # and its sign.
#         cos_rake = np.dot(n_slip, strike_vec)
#         sin_rake = np.dot(n_slip, up_dip_vec)

#         rake = np.degrees(np.arctan2(sin_rake, cos_rake))

#         return strike, dip, rake

#     # --- Calculate for both possible planes ---
#     plane1_sdr = get_sdr(n1, n2)
#     plane2_sdr = get_sdr(n2, n1)

#     result1 = {"strike": plane1_sdr[0], "dip": plane1_sdr[1], "rake": plane1_sdr[2]}
#     result2 = {"strike": plane2_sdr[0], "dip": plane2_sdr[1], "rake": plane2_sdr[2]}

#     return result1, result2


def nodal_to_sdr(n1, n2):
    """
    Calculates strike, dip, and rake for two orthogonal nodal plane vectors.

    This function computes the orientation parameters for two possible fault planes
    given their normal vectors. It assumes a double-couple source model where the
    slip vector on one plane is the normal to the other.

    Args:
        n1 (tuple or list): The (nx, ny, nz) components of the first normal vector.
        n2 (tuple or list): The (nx, ny, nz) components of the second normal vector.

    Returns:
        tuple: A tuple containing two dictionaries, one for each potential fault plane.
               Each dictionary contains the 'strike', 'dip', and 'rake'.
               Returns (None, None) if the input vectors are not orthogonal.

    Conventions Used:
    - Coordinate System: Right-handed North-East-Down (NED).
        - x: North
        - y: East
        - z: Down
    - Strike: 0-360 degrees, measured clockwise from North.
    - Dip: 0-90 degrees.
    - Rake: -180 to 180 degrees. Angle of slip on the fault plane, measured
            counter-clockwise from the strike direction.
    - Normal Vector: The normal to the fault plane is constrained to point
      upwards (z-component <= 0) for calculation consistency.
    """

    # --- Normalize input vectors and check for orthogonality ---
    n1 = np.array(n1, dtype=float)
    n2 = np.array(n2, dtype=float)

    if np.linalg.norm(n1) == 0 or np.linalg.norm(n2) == 0:
        print("Error: Input vectors must have non-zero length.")
        return None, None

    n1 /= np.linalg.norm(n1)
    n2 /= np.linalg.norm(n2)

    if not np.isclose(np.dot(n1, n2), 0.0, atol=1e-4):
        print(f"Error: Input vectors are not orthogonal. Dot product: {np.dot(n1, n2)}")
        return None, None

    def ns2sdr(vec_normal, vec_slip):
        """
        Calcualte strike, dip, rake angles from fault normal vector and slip vector
        Output angles' units in degree
        """
        r2d = 180 / np.pi
        if 1 - np.abs(vec_normal[2]) < 1e-14:
            # strike does not have definition in this case
            dip = 0
            stk = np.arctan2(-vec_slip[0], vec_slip[1])
            rak = np.arctan2(
                np.sin(stk) * vec_slip[0] - np.cos(stk) * vec_slip[1],
                np.cos(stk) * vec_slip[0] + np.sin(stk) * vec_slip[1],
            )
        else:
            dip = np.arctan2(np.sqrt(vec_normal[0] ** 2 + vec_normal[1] ** 2), -vec_normal[2])
            stk = np.arctan2(-vec_normal[0], vec_normal[1])
            rak = np.arctan2(
                -vec_slip[2] / np.sin(dip),
                np.cos(stk) * vec_slip[0] + np.sin(stk) * vec_slip[1],
            )
        if dip >= np.pi * 0.5:
            dip = np.pi - dip
            stk += np.pi
            rak = -rak
        stk *= r2d
        dip *= r2d
        rak *= r2d
        if stk < 0:
            stk = stk + 360
        if rak <= -180:
            rak += 360
        elif rak >= 180:
            rak -= 360
        return stk, dip, rak

    # --- Calculate for both possible planes ---
    plane1_sdr = ns2sdr(n1, n2)
    plane2_sdr = ns2sdr(n2, n1)

    result1 = {"strike": plane1_sdr[0], "dip": plane1_sdr[1], "rake": plane1_sdr[2]}
    result2 = {"strike": plane2_sdr[0], "dip": plane2_sdr[1], "rake": plane2_sdr[2]}

    return result1, result2


# %%
# Step 2a: Feature Transformation
# Transform x -> [x1^2, x2^2, x3^2, sqrt(2)x1x2, sqrt(2)x1x3, sqrt(2)x2x3]
def transform_features(X_data):
    N = X_data.shape[0]
    Z = np.zeros((N, 6))
    Z[:, 0] = X_data[:, 0] ** 2
    Z[:, 1] = X_data[:, 1] ** 2
    Z[:, 2] = X_data[:, 2] ** 2
    Z[:, 3] = np.sqrt(2) * X_data[:, 0] * X_data[:, 1]
    Z[:, 4] = np.sqrt(2) * X_data[:, 0] * X_data[:, 2]
    Z[:, 5] = np.sqrt(2) * X_data[:, 1] * X_data[:, 2]
    return Z


fig, ax = plt.subplots(2, 2, figsize=(10, 8))
for i in range(len(data["azimuth"])):
    x = np.cos(torch.deg2rad(data["azimuth"][i])) * torch.sin(torch.deg2rad(data["takeoff_angle"][i]))
    y = torch.sin(torch.deg2rad(data["azimuth"][i])) * torch.sin(torch.deg2rad(data["takeoff_angle"][i]))
    z = np.cos(torch.deg2rad(data["takeoff_angle"][i]))
    obs = data["phase_polarity"][i]
    X = np.stack([x, y, z], axis=1)
    Z_features = transform_features(X)

    # Step 2b: Train a Linear SVM
    # A more rigorous method would use a QP solver with the Tr(Q)=0 constraint.
    # This approach is a simpler and effective approximation.
    # svm = SVC(kernel="linear", C=10.0)
    svm = LinearSVC(C=10.0, fit_intercept=False)
    svm.fit(Z_features, obs)
    w = svm.coef_[0]

    # Step 2c: Reconstruct the matrix Q and make it traceless
    Q_est_raw = np.array(
        [
            [w[0], w[3] / np.sqrt(2), w[4] / np.sqrt(2)],
            [w[3] / np.sqrt(2), w[1], w[5] / np.sqrt(2)],
            [w[4] / np.sqrt(2), w[5] / np.sqrt(2), w[2]],
        ]
    )
    # Enforce the traceless constraint by projecting Q onto the space of traceless matrices
    Q_est = Q_est_raw - (np.trace(Q_est_raw) / 3.0) * np.identity(3)

    # Step 2d: Find normals from the eigenvectors of Q
    eigenvalues, eigenvectors = np.linalg.eigh(Q_est)

    # Eigenvectors for the most positive and most negative eigenvalues
    v_neg = eigenvectors[:, 0]  # Corresponds to the smallest eigenvalue
    v_pos = eigenvectors[:, 2]  # Corresponds to the largest eigenvalue

    # Combine them to find the estimated normal vectors
    n1_est = (v_pos + v_neg) / np.linalg.norm(v_pos + v_neg)
    n2_est = (v_pos - v_neg) / np.linalg.norm(v_pos - v_neg)

    # Convert to strike, dip, rake
    plane1, plane2 = nodal_to_sdr(n1_est, n2_est)
    print(f"Plane 1 (strike, dip, rake): {plane1}")
    # print(f"Plane 2 (strike, dip, rake): {plane2}")
    print(f"Grund Truth: {strike[i], dip[i], rake[i]}")

    ## prediction

    y_pred = svm.predict(Z_features)
    ax[0, i].scatter(X[:, 0], X[:, 1], c=y_pred, s=12, cmap="RdBu")
    ax[0, i].set_title(f"Ground Truth {i}")
    ax[0, i].set_xlim(-1, 1)
    ax[0, i].set_ylim(-1, 1)
    ax[0, i].set_aspect("equal")

    ##
    x_dense = np.cos(torch.deg2rad(data_dense["azimuth"][i])) * torch.sin(
        torch.deg2rad(data_dense["takeoff_angle"][i])
    )
    y_dense = torch.sin(torch.deg2rad(data_dense["azimuth"][i])) * torch.sin(
        torch.deg2rad(data_dense["takeoff_angle"][i])
    )
    z_dense = np.cos(torch.deg2rad(data_dense["takeoff_angle"][i]))
    X_dense = np.stack([x_dense, y_dense, z_dense], axis=1)
    Z_features_dense = transform_features(X_dense)
    y_pred_dense = svm.predict(Z_features_dense)
    # y_pred_dense = data_dense["phase_polarity"][i]
    ax[1, i].scatter(X_dense[:, 0], X_dense[:, 1], c=y_pred_dense, s=5, cmap="RdBu")
    ax[1, i].set_xlim(-1, 1)
    ax[1, i].set_ylim(-1, 1)
    ax[1, i].set_aspect("equal")

# %%
fig, ax = plt.subplots(2, 2, figsize=(10, 8))
for i in range(len(data["azimuth"])):
    x = torch.cos(torch.deg2rad(data["azimuth"][i])) * torch.sin(torch.deg2rad(data["takeoff_angle"][i]))
    y = torch.sin(torch.deg2rad(data["azimuth"][i])) * torch.sin(torch.deg2rad(data["takeoff_angle"][i]))
    c = data["phase_polarity"][i]
    ax[0, i].scatter(x, y, s=5, c=c, cmap="RdBu")
    ax[0, i].set_xlim(-1, 1)
    ax[0, i].set_ylim(-1, 1)
    ax[0, i].set_aspect("equal")
    ax[0, i].set_title(f"Ground Truth {i}")

for i in range(len(data_dense["azimuth"])):
    x = torch.cos(torch.deg2rad(data_dense["azimuth"][i])) * torch.sin(torch.deg2rad(data_dense["takeoff_angle"][i]))
    y = torch.sin(torch.deg2rad(data_dense["azimuth"][i])) * torch.sin(torch.deg2rad(data_dense["takeoff_angle"][i]))
    c = data_dense["phase_polarity"][i]
    ax[1, i].scatter(x, y, s=5, c=c, cmap="RdBu")
    ax[1, i].set_xlim(-1, 1)
    ax[1, i].set_ylim(-1, 1)
    ax[1, i].set_aspect("equal")
    ax[1, i].set_title(f"Ground Truth {i}")


# %% [markdown]
#

# %%
# n1_est

# %%
# n2_est

# %%
# nx, ny, nz = n1_est

# %%
# dip = np.arccos(nz)

# phi = np.arctan2(-nx, ny)

# d_strike = [np.cos(phi), np.sin(phi), 0]
# d_updip = np.cross(d_strike, n1_est)

# rake = np.arctan2(np.dot(d_updip, n2_est), np.dot(d_strike, n2_est))

# dip = np.rad2deg(dip)
# phi = np.rad2deg(phi)
# rake = np.rad2deg(rake)

# print(f"{dip = }, {phi = }, {rake = }")

# %% [markdown]
#

# %%


# # %%
# plane1, plane2 = nodal_to_sdr(n1_est, n2_est)
# print("Plane 1 (strike, dip, rake):", plane1)
# print("Plane 2 (strike, dip, rake):", plane2)

# %%
