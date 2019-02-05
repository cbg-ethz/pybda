{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "import sklearn"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "feature_dict = {i:label for i,label in zip(\n",
    "                range(4),\n",
    "                  ('sepal length in cm',\n",
    "                  'sepal width in cm',\n",
    "                  'petal length in cm',\n",
    "                  'petal width in cm', ))}\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>sepal length in cm</th>\n",
       "      <th>sepal width in cm</th>\n",
       "      <th>petal length in cm</th>\n",
       "      <th>petal width in cm</th>\n",
       "      <th>class label</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>145</th>\n",
       "      <td>6.7</td>\n",
       "      <td>3.0</td>\n",
       "      <td>5.2</td>\n",
       "      <td>2.3</td>\n",
       "      <td>Iris-virginica</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>146</th>\n",
       "      <td>6.3</td>\n",
       "      <td>2.5</td>\n",
       "      <td>5.0</td>\n",
       "      <td>1.9</td>\n",
       "      <td>Iris-virginica</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>147</th>\n",
       "      <td>6.5</td>\n",
       "      <td>3.0</td>\n",
       "      <td>5.2</td>\n",
       "      <td>2.0</td>\n",
       "      <td>Iris-virginica</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>148</th>\n",
       "      <td>6.2</td>\n",
       "      <td>3.4</td>\n",
       "      <td>5.4</td>\n",
       "      <td>2.3</td>\n",
       "      <td>Iris-virginica</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>149</th>\n",
       "      <td>5.9</td>\n",
       "      <td>3.0</td>\n",
       "      <td>5.1</td>\n",
       "      <td>1.8</td>\n",
       "      <td>Iris-virginica</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "     sepal length in cm  sepal width in cm  petal length in cm  \\\n",
       "145                 6.7                3.0                 5.2   \n",
       "146                 6.3                2.5                 5.0   \n",
       "147                 6.5                3.0                 5.2   \n",
       "148                 6.2                3.4                 5.4   \n",
       "149                 5.9                3.0                 5.1   \n",
       "\n",
       "     petal width in cm     class label  \n",
       "145                2.3  Iris-virginica  \n",
       "146                1.9  Iris-virginica  \n",
       "147                2.0  Iris-virginica  \n",
       "148                2.3  Iris-virginica  \n",
       "149                1.8  Iris-virginica  "
      ]
     },
     "execution_count": 3,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "import pandas as pd\n",
    "\n",
    "df = pd.io.parsers.read_csv(\n",
    "    filepath_or_buffer='https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data',\n",
    "    header=None,\n",
    "    sep=',',\n",
    "    )\n",
    "df.columns = [l for i,l in sorted(feature_dict.items())] + ['class label']\n",
    "df.dropna(how=\"all\", inplace=True) # to drop the empty line at file-end\n",
    "\n",
    "df.tail()\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 22,
   "metadata": {},
   "outputs": [],
   "source": [
    "from sklearn.preprocessing import LabelEncoder\n",
    "\n",
    "X = df.iloc[:,:4].values\n",
    "y = df.iloc[:,4].values\n",
    "\n",
    "enc = LabelEncoder()\n",
    "label_encoder = enc.fit(y)\n",
    "y = label_encoder.transform(y) + 1\n",
    "\n",
    "label_dict = {1: 'Setosa', 2: 'Versicolor', 3:'Virginica'}"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 23,
   "metadata": {},
   "outputs": [],
   "source": [
    "%matplotlib inline"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 24,
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "/Users/simondi/miniconda3/envs/tix/lib/python3.6/site-packages/matplotlib/cbook/__init__.py:424: MatplotlibDeprecationWarning: \n",
      "Passing one of 'on', 'true', 'off', 'false' as a boolean is deprecated; use an actual boolean (True/False) instead.\n",
      "  warn_deprecated(\"2.2\", \"Passing one of 'on', 'true', 'off', 'false' as a \"\n"
     ]
    },
    {
     "data": {
      "image/png": "iVBORw0KGgoAAAANSUhEUgAAA1gAAAGoCAYAAABbkkSYAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAALEgAACxIB0t1+/AAAADl0RVh0U29mdHdhcmUAbWF0cGxvdGxpYiB2ZXJzaW9uIDMuMC4yLCBodHRwOi8vbWF0cGxvdGxpYi5vcmcvOIA7rQAAIABJREFUeJzs3Xt8VOW59//PJYQaiCA8QCuIRMRm66Y2IlKESoaDGKyCsfbgRg5aimLdVrb10Io2VJAtLVhr+eGvxhKpbt1USwAr2RQltuKDrUFUqAVRkCoIykEMKBJyPX/MIjuHSTJkJjOT5Pt+vfJiZh3u+1qLSa651rrXWubuiIiIiIiISOxOSHYAIiIiIiIiLYUKLBERERERkThRgSUiIiIiIhInKrBERERERETiRAWWiIiIiIhInKjAEhERERERiRMVWNIqmdk4M1vZiPVKzGxyHfNOM7MyM2sTe4QiItIaKB+JtDwqsKRFMrNtZjayrvnu/ri7j4pnn+6+3d0z3P1oA7FNMrMX49l3spjZHDP7fvD6XTPrVGXeMDNbbWYfm9m2pAUpIpJEykeJ0UA+utXMNpjZJ2a21cxuTV6k0hqowJJWx8zaJjuGpmJhify9Pg8oNbNuwOfu/nGVeQeB3wJKZCIiESgfxVV9+ciACUBnIBe40cy+m8DYpJVRgSUtXnCEbo2Z3W9me4H8qkftgiRwv5ntDs62vG5m/eppsnfQ3idmttLMugbtZJqZH0uYQR/vVDliNs7MzgIeAi4Ihm/sD5btZGaLzOzD4Mjb9GOJyczamNlcM/soaOfGGv2UmNksM1sDHAL6mNk1ZvZm0Pc7ZnZdlf0RMrP3zOy2YJt3mtnlZnaJmW02s71m9pMo9qsB/wpsAAYAr1ad7+5/dfffAe9E9R8lItLCKR8lLR/Ncfd17l7u7puApcCQaP7PRBpDBZa0Fl8j/EW/OzCrxrxRwFDgy8DJwHeAPfW09W/ANUFb7YAf1VzAzDoAvwJGu/tJwGBgvbu/CVwP/N9g+MbJwSoPAp2APkAO4SNt1wTzvg+MBrKB/sDlEWIaD0wBTgLeBXYDlwIdg3buN7P+VZb/EnAi0BO4G3gYuJrwEcALgbvNrE+kjTezM4NE/DHQNehrCXCZme03s/GRd5uIiKB8lNR8FBRjFwIbI7UpEg8qsKS12OHuDwZHrz6tMe8I4UTwL4C5+5vuvrOetha6++agncWEE00kFUA/M0t3953uHvGPuYUvQv4O8GN3/8TdtwFzCScpgG8DD7j7e+6+D/jPCM0UuvvGYPuOuPsf3f1tD3sBWEk4oVTd5lnufgR4knBieiDofyPhxHNOpHjd/a0gEf8KuIXwkIvNQF93Pzk4ayUiIpEpHyU3H+UT/v67MPKuEomdCixpLf5Z1wx3fx74NTAf2GVmvzGzjvW09UGV14eAjAhtHiScpK4HdprZH83sX+poryvhI4/vVpn2LuGjeQA9asQfaVuqTTOz0Wa2NhhesR+4JOjnmD1VLn4+luB3VZn/aaTtCtp+KWjzx8DPgAPAWcBGM3sq8iaKiEhA+ShJ+cjMbiR8Ru4b7n44Upsi8aACS1oLr3em+6/c/TzCY7i/TBxuzODu/+PuFwGnAP8gPOwhUiwfET6C17vKtNOA94PXO4FTq8zrFam7Yy/M7AvA08AvgC8GR/eeJXyRb8zcfTCQBbzl7p2A6cB9wdHCK+PRh4hIC6Z8lIR8ZGbXAncAI9z9vXj0L1IXFVjS6pnZ+Wb2NTNLI3znu8+Aem9tG0WbXzSzMcHY98NAWZU2dwGnmlk7gODI3WJglpmdZGa9gf8AHguWXwz80Mx6mtnJwO0NdN8O+ALwIVBuZqMJj+uPp6oXEfcHXqm5gJmdYGYnAmnht3bisW0WEZHalI8aJZp8NA64F7jI3XXjJWlyKrBEwhfePgzsIzwUYg/ho22xOIHwePAdwF7CFwrfEMx7nvCY8g/M7KNg2r8TTqbvAC8C/0X4FucEsa0EXiecRJ4Fyqkj6br7J8BNhBPhPsIXQS+LcXtqOg9YF7zuD5RGWGYo4aEdzxI+Avop4e0QEZHIlI+OXzT5aCbwf4C/BXdMLDOzh+Ich0glc6/3TLWIpJjgCOBD7t67wYVFRESaiPKRSGQ6gyWS4swsPXgmSFsz6wn8lPBtaEVERBJG+UgkOjqDJZLizKw98ALh2/Z+CvwR+KG7H0hqYCIi0qooH4lERwWWiIiIiIhInGiIoIiIiIiISJy0TXYAUdJpNhGR1i0uz82JA+UjEZHWK6pcpDNYIiIiIiIicaICS0REREREJE5UYImIiIiIiMRJc7kGS0QkqQ4dOsT+/fuTHUarkJaWRpcuXWjTpk2yQxERSSlHjx5l7969HDlyJNmhtHix5KLmcpv2ZhGkiLRcu3btonPnzrRr1y7ZobRo7k5ZWRmfffYZ3bp1qzpLN7kQkVbvww8/5MQTTyQjIwOzVPmz2PLEmos0RFBEJApHjx4lLS0t2WG0eGZGRkaGjs6KiERw5MgRFVcJEGsuUoElIhIlJbTE0H4WEamb/kYmRiz7WQWWiEgKC4VClJeXx9zO448/zqBBg7jwwguZMmVKncsVFRWxd+/emPsTEZGWRfkoerrJhYjIccrPT+76jfHAAw/w0ksv0bZtW/bt21fnckVFRfTr148uXbokMDoREWkM5aPUpDNYIiIpoqKigsmTJ5OTk8Po0aOrzSsuLiYnJ4cBAwawaNEiAObPn8+gQYMYNmwY69atY8mSJQwcOJDhw4fz7LPPVlv/4MGDvPzyy1RUVNC5c2cAtmzZwqhRo8jJyWHmzJls376d4uJixo0bx89//nO2b9/O8OHDGTJkCPfdd1/EPtevX09OTg6DBg3i3nvvTcBeEhGRpqZ8FBudwRIRSRFLly6le/fuFBQUUFFRUW3e0KFDyc3Npby8nFAoxIQJE1i6dCmrV68mPT0dd2fevHksXryYzMxMat4htrCwkFmzZvHGG29w2223cd1113HnnXfyyCOP0KtXL6666ipOOOEEcnNzmT59On379uUHP/gBM2bM4MILL+Tiiy9m/Pjxtfr87LPPKCkpwcwYNmwY06ZNIz09PZG7TURE4kz5KDYqsEREUsTmzZsZPHgwACecUH2AQWlpKTNmzODIkSNs3LgRgBkzZjB16lTatWvHPffcw/Tp05k5cybl5eXceeednHnmmZXrn3/++RQVFXHo0CGGDRvGuHHj2LRpE+PHjwdg//79vP/++9X6fPvtt+nfvz8A5557Llu3bq3V5549e7jllls4dOgQmzZtYvfu3fTu3bvJ9pGIiDQ95aPYaIigiEiKyMrKYu3atQC1jhjOmTOHgoICVq1aRadOnQDIzs6msLCQUChEYWEhvXv3pqCggClTpjBv3rxq67/11lsAtG/fvvKIXlZWFk888QQlJSWUlpZy/vnnk5aWxtGjRwHo06cPpaWlALz66qtkZmbW6nPBggXcfvvtvPDCC/Tt27fWkUoREWl+lI9iozNYIiIpYsyYMSxfvpyhQ4eSkZFRbdx6Xl4eY8eOJTs7u3LM+vXXX8/WrVs5fPgwCxcuJD8/n7Vr11JWVsbcuXOrtT1t2rTKi4mvvPJKMjIymDVrFtdeey2HDx8mLS2Np59+mosvvpgbbriBb33rW9x+++1MnDiRzz//nMsuu4yePXsyceLEan1u376dG2+8kbPPPlsPYRYRaSGUj2JjzeRoY7MIUkRarh07dtCjR49kh9FqRNjfqfLgF+UjEUka5aLEamwu0hBBERERERGROFGBJSIiIiIiEicqsEREREREROJEBZaIiIiIiEicqMASERERERGJExVYIiIpLBQKUV5eHlMbxcXF3HrrrZXv9+zZw0UXXdSotm6++ebK55JE4+tf/3qj+hERkdSifBQ9PQdLROR45ecnd/3jNGLECO66667K98uWLWPMmDENrldRUcEJJ1Q/DvfLX/4y7vFF6kdERKKgfBRX8cpHKrAkLmL5/Uzw77ZIyqqoqGDKlCm89dZbtG/fnhUrVlTOKy4uZvbs2Rw8eJCbbrqJCRMmMH/+fH73u9+Rnp7O3Llzeffdd5k9ezYZGRn86Ec/4pJLLgEgLS2NrKwsNmzYQL9+/SgqKuLXv/417s4NN9zApk2bSE9P57HHHuO1115j3rx5uDuTJ0/m4Ycf5uDBg3Tr1o3FixcTCoVYtWoVH330Eddccw2ffvopF1xwAbNnz+a+++5j2bJlfOELX6CwsJDTTjutMv5Vq1Yxffp0AGbOnMnIkSMJhUIMHDiQHTt28NhjjyV2Z4vEUX5JfuPXDTV+XZGmonwUGxVYIiIpYunSpXTv3p2CggIqKiqqzRs6dCi5ubmUl5cTCoWYMGECS5cuZfXq1aSnp+PuzJs3j8WLF5OZmUnNh8hfccUVFBUVcfrpp7Nv3z569erF8uXLOe2001iwYAErVqzgoYce4oILLuDzzz+nuLiYLVu20LVrV5555pla7c2ePZtp06YxatQoKioq+OCDD3j++edZs2YNL774IrNnz2bBggWVy+fn57Ny5UoAcnNzGTlyJAB5eXlccMEFTbE7RUSkkZSPYqMxGSIiKWLz5s0MHjwYoNYQhdLSUkaOHMmIESPYuHEjADNmzGDq1KlMmTKF3bt3M336dGbOnMmkSZPYsmVLtfVzc3NZuXIlK1asIDc3F4A333yTJ598klAoxKxZs9i7dy8A/fv3B6Bv37585StfYdy4cdx///31xrpt2zbOOeccAAYMGFCrfzOjY8eOdOzYkTZt2lROP++88xq/w0REpEkoH8VGBZaISIrIyspi7dq1ALWOGM6ZM4eCggJWrVpFp06dAMjOzqawsJBQKERhYSG9e/emoKCAKVOmMG/evGrrt2/fnq5du/Lggw+Sl5dX2d+ECRMoKSnhxRdf5N577wX+N5kePnyYadOm8fjjj1NcXMyuXbvqjDUzM5PXXnsNgFdeeYUzzjijWv8VFRUcOHCAAwcOVLsoWddeiYikHuWj2GiIoIhIihgzZgzLly9n6NChZGRk8Oyzz1bOy8vLY+zYsWRnZ9O5c2cArr/+erZu3crhw4dZuHAh+fn5rF27lrKyMubOnVur/by8PGbNmsVZZ51V2d9NN93E8OHDgfAdmTp27Fi5/Lvvvsv3vvc9ysvL6dOnD927d6+cd8cddzBx4kRmzpzJ4MGDuffeexk2bBiDBw+mXbt2PProo9X6vvvuuxk1ahTuzs9+9rP47TQREYk75aPYWM1xjHFr2Oy3wKXAbnfvF0zLB74PfBgs9hN3fzZyC9U0TZASN7rJhbR0O3bsoEePHskOo9WIsL+tsW0pH0lT000uJFGUixKrsbmoKcdmFAK5Eabf7+7ZwU80yUxERCQWhSgfiYhIgjRZgeXufwb2NlX7IiIi0VA+EhGRRErG1cU3mtnrZvZbM+uchP5FRERA+UhERJpAogusBcAZQDawE6h91ZuIiEjTUz4SEZEmkdACy913uftRd68AHgYGJrJ/ERERUD4SEZGmk9ACy8xOqfI2D9iQyP5FRJqbUChEeXl5TG0UFxdz6623Vr7fs2cPF110EevXr+eRRx6Jqo3CwkJKS0sjzjuedlKF8pGIyPFRPopekz0Hy8yeAEJAVzN7D/gpEDKzbMK3ud0GXNdU/YuINJVYbskMib8t84gRI7jrrrsq3y9btowxY8aQnZ1NdnZ2tWUrKioiPmxx0qRJdbYfqZ1UonwkIi2V8lF1qZKPmvIugle5+ynunubup7r7I+4+3t2/4u7nuPsYd9/ZVP2LiDQ3FRUVTJ48mZycHEaPHl1tXnFxMTk5OQwYMIBFixYBMH/+fAYNGsSwYcNYt24dS5YsYeDAgQwfPrzaQyHT0tLIyspiw4bwSZqioiIuv/xySkpKmD59OgBf/epXufrqq5kzZw4vv/wy/fv356qrrqJ///4A5Ofns2rVKkpKShg7diyXXXYZQ4YMoaysrFo7CxYsqIxp06ZNEeNONOUjEZHjo3wUmyY7gyUiIsdn6dKldO/enYKCAioqKqrNGzp0KLm5uZSXlxMKhZgwYQJLly5l9erVpKen4+7MmzePxYsXk5mZSc2HyF9xxRUUFRVx+umns2/fPnr16sXbb79dOf+9997jpZdeokOHDlx66aUsW7aMzp0707t374ixLl++nFmzZvHcc8/RqVMnAHbv3s3vf/971qxZQ5s2baioqKBXr1614hYRkdSmfBSbZNymXUREIti8eTODBw8GqDUsorS0lJEjRzJixAg2btwIwIwZM5g6dSpTpkxh9+7dTJ8+nZkzZzJp0iS2bNlSbf3c3FxWrlzJihUryM2t/czdrKwsOnToAMCBAwc49dRT6dChA2eeeWatZfv16wdAz5492b9/f+X0rVu30r9/f9q0aVO5DZHiFhGR1KZ8FBsVWCIiKSIrK4u1a9cC1DpiOGfOHAoKCli1alXlEbrs7GwKCwsJhUIUFhbSu3dvCgoKmDJlCvPmzau2fvv27enatSsPPvggeXl5tfqumkA7duzIjh07OHToUK3ECGBmla+rHpns06cPr776amXsFRUVEeMWEZHUpnwUGw0RFBFJEWPGjGH58uUMHTqUjIyMauPW8/LyGDt2LNnZ2XTuHH4m7vXXX8/WrVs5fPgwCxcuJD8/n7Vr11JWVsbcubUf65SXl8esWbM466yz6o3jrrvu4rLLLqNv37706tUr6vi7devGN7/5TQYPHkx6ejoPPfRQxLhFRCS1KR/FxmqOi0xRzSLI1iw/PznriiTKjh076NGjR7LDSIjy8nLatm3LwYMHGTVqFGvWrEl4DBH2t9W1bIIpH0ktsdzJLdF3cZPmrTXlIkh+PmpsLtIQQRERqWbNmjXk5ORw4YUXVnteiYiISCI113ykIYIiIlJNTk4OL7zwQrLDEBGRVq655iOdwRIRiVIzGVLd7Gk/i4jUTX8jEyOW/awCS0QkCm3atOHIkSPJDqPFc3fKyspIS0tLdigiIiknLS2NsrIyFVlNLNZcpCGCIiJROOmkk/joo4+SHUarkJaWRpcuXZIdhohIyunSpQt79+7lk08+SXYoLV4suUgFlohIFNq3b0/79u2THYaIiLRibdq0oVu3bskOQxqgIYIiIiIiIiJxogJLREREREQkTlRgiYiIiIiIxIkKLBERERERkThRgSUiIiIiIhInKrBERERERETiRAWWiIiIiIhInKjAEhERERERiRMVWCIiIiIiInGiAktERERERCROVGCJiIiIiIjEiQosERERERGROFGBJSIiIiIiEicqsEREREREROJEBZaIiIiIiEicqMASERERERGJk7bJDkBERESkOdtWWNL4lUPxikJEUoXOYImIiIiIiMRJVAWWmT0XzTQREREREZHWrN4hgmZ2ItAe6GpmnQELZnUEejRxbCIiIiIiIs1KQ9dgXQfcTLiYKuV/C6wDwPwmjEtERERERKTZqXeIoLs/4O6nAz9y9z7ufnrw81V3/3V965rZb81st5ltqDKti5n9yczeCv7tHKftEBERiUj5SEREEimqa7Dc/UEzG2xm/2ZmE479NLBaIZBbY9odwHPufibwXPBeRESkKRWifCQiIgkS7U0ufgf8Avg6cH7wM6C+ddz9z8DeGpPHAo8Grx8FLj+eYEVERI6X8pGIiCRStM/BGgCc7e4eY39fdPedAO6+08y6x9ieSOPk5ydnXRFJFcpHIiLSJKJ9DtYG4EtNGYiIiIiIiEhzF+0ZrK7A383sr8DhYxPdfcxx9rfLzE4JjhaeAuw+zvVFRETiQflIRESaRLQFVn6c+lsGTAT+M/h3aZzaFREROR7KRyIi0iSiKrDc/YXjbdjMngBChB9S/B7wU8KJbLGZfQ/YDnzreNsVERE5HspHIiKSSFEVWGb2CXDsBhftgDTgoLt3rGsdd7+qjlkjjitCERGRGCgfiYhIIkV7Buukqu/N7HJgYJNEJCIiIiIi0kxFexfBaty9CBge51hERERERESatWiHCF5R5e0JhJ+LFeszsUREREQkwRr7OEc9BlIkOtHeRfCyKq/LgW3A2LhHIyIiIiIi0oxFew3WNU0diIiIiIiISHMX1TVYZnaqmS0xs91mtsvMnjazU5s6OBERERERkeYk2ptcLCT8UMYeQE9geTBNREREREREAtEWWN3cfaG7lwc/hUC3JoxLRERERESk2Ym2wPrIzK42szbBz9XAnqYMTEREREREpLmJtsC6Fvg28AGwE7gS0I0vREREREREqoj2Nu33ABPdfR+AmXUBfkG48BJpXZLxAJFGrpsfiqHLUOP6FBFJpvyS/Matp795DUpCGhNplqI9g3XOseIKwN33Auc2TUgiIiIiIiLNU7QF1glm1vnYm+AMVrRnv0RERERERFqFaIukucBLZvYU4ISvx5rVZFGJiIiIiIg0Q1EVWO6+yMxeAYYDBlzh7n9v0shERERERESamaiH+QUFlYoqERERERGROkR7DZaIiIiIiIg0QAWWiIiIiIhInOhOgC1QMh7TJBIPjX1+DegZNiIpp7k9NElJUETiRGewRERERERE4kQFloiIiIiISJyowBIREREREYkTFVgiIiIiIiJxogJLREREREQkTlRgiYiIiIiIxIkKLBERERERkTjRc7BEREQk7vIpiWHdGJQ0tt9QLL2KiFTSGSwREREREZE4UYElIiIiIiISJyqwRERERERE4kQFloiIiIiISJwk5SYXZrYN+AQ4CpS7+4BkxCEiIq2b8pGIiMRbMu8iOMzdP0pi/yIiIqB8JCIicaQhgiIiIiIiInGSrALLgZVmVmpmU5IUg4iIiPKRiIjEVbKGCA5x9x1m1h34k5n9w93/nKRYUlJ+frIjSH2x7KMYVm1eGv3ATciPYS/lhxq/rkiCKR+lolaUBEON3NaSVrSPRJqbpJzBcvcdwb+7gSXAwGTEISIirZvykYiIxFvCCywz62BmJx17DYwCNiQ6DhERad2Uj0REpCkkY4jgF4ElZnas//9y9+IkxCEiIq2b8pGIiMRdwgssd38H+Gqi+xUREalK+UhERJqCbtMuIiIiIiISJyqwRERERERE4kQFloiIiIiISJwk6zlYkoKS9UiN5vYoj3xKGrle4vtMlvyS/MatGMNzuwg1ftXGavR2kpxnhTU2Xj3XTBKtuf3Nk6bV2O8Jze37hbQcOoMlIiIiIiISJyqwRERERERE4kQFloiIiIiISJyowBIREREREYkTFVgiIiIiIiJxogJLREREREQkTlRgiYiIiIiIxImeg9XEWsszGEIxPA+opJk9Y2fbtmRH0AzE8jyrRtIznkTq0VqSUTOUua2kUevF8hy+2J7M2MgeE9+lSNLoDJaIiIiIiEicqMASERERERGJExVYIiIiIiIicaICS0REREREJE5UYImIiIiIiMSJCiwREREREZE4UYElIiIiIiISJ3oOlrRKMT2mKbOR6zW3h4Ak4VlWItKA5vZ3pBnJpyTZIRyX2P5E5zdqrVASnp8FUNLIfvOT8PuiX1EBncESERERERGJGxVYIiIiIiIicaICS0RE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\n",
      "text/plain": [
       "<Figure size 864x432 with 4 Axes>"
      ]
     },
     "metadata": {
      "needs_background": "light"
     },
     "output_type": "display_data"
    }
   ],
   "source": [
    "from matplotlib import pyplot as plt\n",
    "import numpy as np\n",
    "import math\n",
    "\n",
    "fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(12,6))\n",
    "\n",
    "for ax,cnt in zip(axes.ravel(), range(4)):  \n",
    "\n",
    "    # set bin sizes\n",
    "    min_b = math.floor(np.min(X[:,cnt]))\n",
    "    max_b = math.ceil(np.max(X[:,cnt]))\n",
    "    bins = np.linspace(min_b, max_b, 25)\n",
    "\n",
    "    # plottling the histograms\n",
    "    for lab,col in zip(range(1,4), ('blue', 'red', 'green')):\n",
    "        ax.hist(X[y==lab, cnt],\n",
    "                   color=col,\n",
    "                   label='class %s' %label_dict[lab],\n",
    "                   bins=bins,\n",
    "                   alpha=0.5,)\n",
    "    ylims = ax.get_ylim()\n",
    "\n",
    "    # plot annotation\n",
    "    leg = ax.legend(loc='upper right', fancybox=True, fontsize=8)\n",
    "    leg.get_frame().set_alpha(0.5)\n",
    "    ax.set_ylim([0, max(ylims)+2])\n",
    "    ax.set_xlabel(feature_dict[cnt])\n",
    "    ax.set_title('Iris histogram #%s' %str(cnt+1))\n",
    "\n",
    "    # hide axis ticks\n",
    "    ax.tick_params(axis=\"both\", which=\"both\", bottom=\"off\", top=\"off\",  \n",
    "            labelbottom=\"on\", left=\"off\", right=\"off\", labelleft=\"on\")\n",
    "\n",
    "    # remove axis spines\n",
    "    ax.spines[\"top\"].set_visible(False)  \n",
    "    ax.spines[\"right\"].set_visible(False)\n",
    "    ax.spines[\"bottom\"].set_visible(False)\n",
    "    ax.spines[\"left\"].set_visible(False)    \n",
    "\n",
    "axes[0][0].set_ylabel('count')\n",
    "axes[1][0].set_ylabel('count')\n",
    "\n",
    "fig.tight_layout()       \n",
    "\n",
    "plt.show()\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 25,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Mean Vector class 1: [5.006 3.418 1.464 0.244]\n",
      "\n",
      "Mean Vector class 2: [5.936 2.77  4.26  1.326]\n",
      "\n",
      "Mean Vector class 3: [6.588 2.974 5.552 2.026]\n",
      "\n"
     ]
    }
   ],
   "source": [
    "mean_vectors = []\n",
    "for cl in range(1,4):\n",
    "    mean_vectors.append(np.mean(X[y==cl], axis=0))\n",
    "    print('Mean Vector class %s: %s\\n' %(cl, mean_vectors[cl-1]))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 27,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "within-class Scatter Matrix:\n",
      " [[38.9562 13.683  24.614   5.6556]\n",
      " [13.683  17.035   8.12    4.9132]\n",
      " [24.614   8.12   27.22    6.2536]\n",
      " [ 5.6556  4.9132  6.2536  6.1756]]\n"
     ]
    }
   ],
   "source": [
    "S_W = np.zeros((4,4))\n",
    "for cl,mv in zip(range(1,4), mean_vectors):\n",
    "    class_sc_mat = np.zeros((4,4))\n",
    "    for row in X[y == cl]:\n",
    "        row, mv = row.reshape(4,1), mv.reshape(4,1)\n",
    "        class_sc_mat += (row - mv).dot((row - mv).T)\n",
    "    S_W += class_sc_mat \n",
    "print('within-class Scatter Matrix:\\n', S_W)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 28,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "between-class Scatter Matrix:\n",
      " [[ 63.21213333 -19.534      165.16466667  71.36306667]\n",
      " [-19.534       10.9776     -56.0552     -22.4924    ]\n",
      " [165.16466667 -56.0552     436.64373333 186.90813333]\n",
      " [ 71.36306667 -22.4924     186.90813333  80.60413333]]\n"
     ]
    }
   ],
   "source": [
    "overall_mean = np.mean(X, axis=0)\n",
    "\n",
    "S_B = np.zeros((4,4))\n",
    "for i,mean_vec in enumerate(mean_vectors):  \n",
    "    n = X[y==i+1,:].shape[0]\n",
    "    mean_vec = mean_vec.reshape(4,1) # make column vector\n",
    "    overall_mean = overall_mean.reshape(4,1) # make column vector\n",
    "    S_B += n * (mean_vec - overall_mean).dot((mean_vec - overall_mean).T)\n",
    "\n",
    "print('between-class Scatter Matrix:\\n', S_B)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 29,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "\n",
      "Eigenvector 1: \n",
      "[[-0.20490976]\n",
      " [-0.38714331]\n",
      " [ 0.54648218]\n",
      " [ 0.71378517]]\n",
      "Eigenvalue 1: 3.23e+01\n",
      "\n",
      "Eigenvector 2: \n",
      "[[-0.00898234]\n",
      " [-0.58899857]\n",
      " [ 0.25428655]\n",
      " [-0.76703217]]\n",
      "Eigenvalue 2: 2.78e-01\n",
      "\n",
      "Eigenvector 3: \n",
      "[[-0.8843662 ]\n",
      " [ 0.28544073]\n",
      " [ 0.2580474 ]\n",
      " [ 0.26425659]]\n",
      "Eigenvalue 3: 3.42e-15\n",
      "\n",
      "Eigenvector 4: \n",
      "[[-0.22342193]\n",
      " [-0.25229799]\n",
      " [-0.32596888]\n",
      " [ 0.88327383]]\n",
      "Eigenvalue 4: 1.15e-14\n"
     ]
    }
   ],
   "source": [
    "eig_vals, eig_vecs = np.linalg.eig(np.linalg.inv(S_W).dot(S_B))\n",
    "\n",
    "for i in range(len(eig_vals)):\n",
    "    eigvec_sc = eig_vecs[:,i].reshape(4,1)   \n",
    "    print('\\nEigenvector {}: \\n{}'.format(i+1, eigvec_sc.real))\n",
    "    print('Eigenvalue {:}: {:.2e}'.format(i+1, eig_vals[i].real))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 30,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Eigenvalues in decreasing order:\n",
      "\n",
      "32.27195779972981\n",
      "0.27756686384003953\n",
      "1.1483362279322388e-14\n",
      "3.422458920849769e-15\n"
     ]
    }
   ],
   "source": [
    "# Make a list of (eigenvalue, eigenvector) tuples\n",
    "eig_pairs = [(np.abs(eig_vals[i]), eig_vecs[:,i]) for i in range(len(eig_vals))]\n",
    "\n",
    "# Sort the (eigenvalue, eigenvector) tuples from high to low\n",
    "eig_pairs = sorted(eig_pairs, key=lambda k: k[0], reverse=True)\n",
    "\n",
    "# Visually confirm that the list is correctly sorted by decreasing eigenvalues\n",
    "\n",
    "print('Eigenvalues in decreasing order:\\n')\n",
    "for i in eig_pairs:\n",
    "    print(i[0])\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 31,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Variance explained:\n",
      "\n",
      "eigenvalue 1: 99.15%\n",
      "eigenvalue 2: 0.85%\n",
      "eigenvalue 3: 0.00%\n",
      "eigenvalue 4: 0.00%\n"
     ]
    }
   ],
   "source": [
    "print('Variance explained:\\n')\n",
    "eigv_sum = sum(eig_vals)\n",
    "for i,j in enumerate(eig_pairs):\n",
    "    print('eigenvalue {0:}: {1:.2%}'.format(i+1, (j[0]/eigv_sum).real))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 33,
   "metadata": {},
   "outputs": [],
   "source": [
    "W = np.hstack((eig_pairs[0][1].reshape(4,1), eig_pairs[1][1].reshape(4,1)))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 34,
   "metadata": {},
   "outputs": [],
   "source": [
    "X_lda = X.dot(W)\n",
    "assert X_lda.shape == (150,2), \"The matrix is not 150x2 dimensional.\""
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 35,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "image/png": "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ggsu4LrrruPdd9/llFNOAVyQ4siRI/ucu3btWg4++GDGjx8PwNy5c7n99tu58sorKS0t5bLLLuOMM87gzDPPBGDjxo1ccMEFbNmyhfb2dg4++OD4BU8iNuIwDCOnWL4c2tth8GD3NxGjjsLCQjweDz/+8Y+57bbbeOSRRzjiiCOora2ltraWd955h2eeeabPeeEWyisqKuK1117jvPPO49FHH+X0008H4KqrruLKK6/knXfe4fe//z2tra0DFz4JmOIwjGxm2DBnCA/+DBuWbsnSgn+0UVXltquq3KhjILaOtWvXsn79+u7t2tpaJk2axPbt26mpqQFckOKqVasAGDx4MM3NzQBMnDiRuro63n//fQDuu+8+TjzxRLxeL01NTcycOZPf/OY31NbWAtDU1MTo0aMB+POf/xy/0EnGpqoMI5t55ZV0S5BR+EcbPjs2JSU9o46zzoqvTq/Xy1VXXcWuXbsoKiri0EMP5Q9/+AP/8R//wbe+9S2ampro6Ojg6quv5ogjjuCSSy7h8ssvp6ysjJqaGv70pz9x/vnn09HRwbHHHsvll19OQ0MDs2bNorW1FVXl17/+NQALFy7k/PPPZ/To0UyfPp2PPvooQd9MYjHFYRhGzvD226AKdXW999fWxq84jjnmGF5++eU++4cNG8YLL7zQZ/95553Heeed17190kkn8dZbb/UqM3LkSF577bU+586aNYtZs2bFJ2gKMcVhGEbOcP316ZYgPzAbh2EYhhETpjgMwzCMmDDFYRiGYcREWhSHiJwvIqtEpEtEpoUpc6CILBeR1b6y3061nIZhGEZf0jXieBeYDfR1SeihA/ieqk4CpgP/KSKHp0I4wzAMIzxpURyqulpV1/ZTZouqvun7vxlYDYxOhXyGYRh+PB4PTz/9dK99v/nNb7jiiisGVO8NN9zAsmXLYj6vurq6O0VJupBwIfEpubhINTBfVd/op9w43Ohksqru7q/empoa9Weg7A+v10v5QBLZZDn53H5re3a0vaKigv322y+hdba3tzNo0KCoyv7v//4vb731Frfcckv3vnPPPZdrrrmG4447LuK5qoqqUlCQuD76K6+8wl133cUf//jHqMp3dHRQVNQTedHe3o7X62X37t6vUo/HE/3SgP6GJfoDLMNNSQV/ZgWUqQam9VNPObACmB3D9aNm+fLlsRTPOfK5/db27GDTpk1a31yvyz9aro+uflSXf7Rc65vrQxf+wQ9U587t+/nBD3oV++ijj6K+/o4dO3TYsGHa2trafe6BBx6oXV1devPNN+u0adP0yCOP1BtuuKH7+MSJE/Wb3/ymTp06Vevq6nTu3Ll6xBFH6OTJk/VXv/qVqqrOnTtX//73v6uq6muvvaYzZszQKVOm6LHHHqu7d+/WlpYWveSSS3Ty5Mk6depUfe6551TV3bszzjhDVVV37typs2bN0iOPPFKPP/54ffvtt1VV9Uc/+pH++7//u55yyil64YUX9mn7pk2bQjU16vd70gIAVfXkgdYhIsXAI8ADqrpo4FIZhpFtNLQ0sL5pPaVFpVSUVNCyt4WXP3mZCftPYNun22hqbWJI6RAmDZvEiPp6GDeubyXBoeQxsP/++3Pcccfx1FNPMWvWLB588EEuuOACnn32WdavX89rr72GqnL22WfzwgsvMHbsWNauXcuf/vQn7rjjDlasWMGmTZt49913Adi1a1ev+tvb27ngggt46KGHOPbYY9m9ezdlZWX89re/BeCdd95hzZo1nHrqqaxbt67XuT/60Y846qijePTRR3nuuef4t3/7t+68VytWrOCll16irKws7raHI2PdccWtqP5HYLWq/ird8hiGkR42NG2gtKiUsuIyRISy4jK6tIvnNzxPy96WXsqkZW9LUmS48MILefDBBwF48MEHufDCC3nmmWd45plnOOqoozj66KNZs2ZNdzLEgw46iOm+5Xs/85nP8OGHH3LVVVfx1FNPUVFR0avutWvXMnLkSI499ljATc0VFRXx0ksvcfHFFwMuWeJBBx3UR3EElvnSl77Ezp07aWpqAuDss89OitKA9LnjnisiG4EZwFIRedq3f5SIPOkr9jngYuBLIlLr+8xMh7yGYaSPPe17KC0q7bVvd/tuurq6eimT0qJSmtqakiLDOeecwz//+U/efPNNWlpaOProo1FVrrnmmu7U6u+//z6XXnopAPvuu2/3uZWVlbz99tt4PB5uv/12Lrvssl51qyqun0yf/f0Rqoy/rkAZEk26vKoWq+oYVS1R1RGqeppv/2ZVnen7/yVVFVWdoqpTfZ8nI9dsGEause+gfWnt6L0uxaftn7JP8T699pUWldLeGX4t8IFQXl6Ox+Nh3rx5XHjhhQCcdtpp3HPPPXh9Ods3bdrEtm3b+py7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\n",
      "text/plain": [
       "<Figure size 432x288 with 1 Axes>"
      ]
     },
     "metadata": {
      "needs_background": "light"
     },
     "output_type": "display_data"
    }
   ],
   "source": [
    "from matplotlib import pyplot as plt\n",
    "\n",
    "def plot_step_lda():\n",
    "\n",
    "    ax = plt.subplot(111)\n",
    "    for label,marker,color in zip(\n",
    "        range(1,4),('^', 's', 'o'),('blue', 'red', 'green')):\n",
    "\n",
    "        plt.scatter(x=X_lda[:,0].real[y == label],\n",
    "                y=X_lda[:,1].real[y == label],\n",
    "                marker=marker,\n",
    "                color=color,\n",
    "                alpha=0.5,\n",
    "                label=label_dict[label]\n",
    "                )\n",
    "\n",
    "    plt.xlabel('LD1')\n",
    "    plt.ylabel('LD2')\n",
    "\n",
    "    leg = plt.legend(loc='upper right', fancybox=True)\n",
    "    leg.get_frame().set_alpha(0.5)\n",
    "    plt.title('LDA: Iris projection onto the first 2 linear discriminants')\n",
    "\n",
    "    # hide axis ticks\n",
    "    plt.tick_params(axis=\"both\", which=\"both\", bottom=\"off\", top=\"off\",  \n",
    "            labelbottom=\"on\", left=\"off\", right=\"off\", labelleft=\"on\")\n",
    "\n",
    "    # remove axis spines\n",
    "    ax.spines[\"top\"].set_visible(False)  \n",
    "    ax.spines[\"right\"].set_visible(False)\n",
    "    ax.spines[\"bottom\"].set_visible(False)\n",
    "    ax.spines[\"left\"].set_visible(False)    \n",
    "\n",
    "    plt.grid()\n",
    "    plt.tight_layout\n",
    "    plt.show()\n",
    "\n",
    "plot_step_lda()\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (Tix)",
   "language": "python",
   "name": "tix"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.6.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
