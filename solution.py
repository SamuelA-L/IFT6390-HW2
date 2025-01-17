import numpy as np


class SVM:
    def __init__(self, eta, C, niter, batch_size, verbose):
        self.eta = eta
        self.C = C
        self.niter = niter
        self.batch_size = batch_size
        self.verbose = verbose

    def make_one_versus_all_labels(self, y, m):
        """
        y : numpy array of shape (n,)
        m : int (num_classes)
        returns : numpy array of shape (n, m)
        """
        n = len(y)
        k = 0
        ans = (np.ones((n, m))*(-1)).astype('int')
        for i in range(n):
            k = y[i]
            ans[i, k] = 1

        return ans


    def compute_loss(self, x, y):
        """
        x : numpy array of shape (minibatch size, num_features)
        y : numpy array of shape (minibatch size, num_classes)
        returns : float
        """
        n, m = x.shape
        hinge_loss = 1/n * np.sum(np.maximum(0, 2 - (x @ self.w) * y)**2)
        regularisation_loss = self.C/2 * np.sum(np.linalg.norm(self.w, ord=2)**2)
        loss = float(hinge_loss + regularisation_loss)

        return loss

    def compute_gradient(self, x, y):
        """
        x : numpy array of shape (minibatch size, num_features)
        y : numpy array of shape (minibatch size, num_classes)
        returns : numpy array of shape (num_features, num_classes)
        """
        n, m = x.shape
        maxes = np.maximum(0, 2 - (x @ self.w) * y)
        regularization_grad = self.C * self.w
        a = 2 - (x @ self.w) * y
        ones_or_zeros = (a > 0).astype(int)
        loss_grad = -2/n * (np.transpose(x) @ (y * maxes * ones_or_zeros))

        return loss_grad + regularization_grad


    # Batcher function
    def minibatch(self, iterable1, iterable2, size=1):
        l = len(iterable1)
        n = size
        for ndx in range(0, l, n):
            index2 = min(ndx + n, l)
            yield iterable1[ndx: index2], iterable2[ndx: index2]

    def infer(self, x):
        """
        x : numpy array of shape (num_examples_to_infer, num_features)
        returns : numpy array of shape (num_examples_to_infer, num_classes)
        """
        y = x @ self.w
        pred = np.argmax(y, axis=1)

        return self.make_one_versus_all_labels(pred, y.shape[1])

    def compute_accuracy(self, y_inferred, y):
        """
        y_inferred : numpy array of shape (num_examples, num_classes)
        y : numpy array of shape (num_examples, num_classes)
        returns : float
        """
        true = np.argmax(y, axis=1)
        pred = np.argmax(y_inferred, axis=1)
        good = np.sum(pred == true)

        return good/len(y)


    def fit(self, x_train, y_train, x_test, y_test):
        """
        x_train : numpy array of shape (number of training examples, num_features)
        y_train : numpy array of shape (number of training examples, num_classes)
        x_test : numpy array of shape (number of training examples, nujm_features)
        y_test : numpy array of shape (number of training examples, num_classes)
        returns : float, float, float, float
        """
        self.num_features = x_train.shape[1]
        self.m = y_train.max() + 1
        y_train = self.make_one_versus_all_labels(y_train, self.m)
        y_test = self.make_one_versus_all_labels(y_test, self.m)
        self.w = np.zeros([self.num_features, self.m])

        train_losses = []
        train_accs = []
        test_losses = []
        test_accs = []

        for iteration in range(self.niter):
            # Train one pass through the training set
            for x, y in self.minibatch(x_train, y_train, size=self.batch_size):
                grad = self.compute_gradient(x, y)
                self.w -= self.eta * grad

            # Measure loss and accuracy on training set
            train_loss = self.compute_loss(x_train, y_train)
            y_inferred = self.infer(x_train)
            train_accuracy = self.compute_accuracy(y_inferred, y_train)

            # Measure loss and accuracy on test set
            test_loss = self.compute_loss(x_test, y_test)
            y_inferred = self.infer(x_test)
            test_accuracy = self.compute_accuracy(y_inferred, y_test)

            if self.verbose:
                print(f"Iteration {iteration} | Train loss {train_loss:.04f} | Train acc {train_accuracy:.04f} |"
                      f" Test loss {test_loss:.04f} | Test acc {test_accuracy:.04f}")

            # Record losses, accs
            train_losses.append(train_loss)
            train_accs.append(train_accuracy)
            test_losses.append(test_loss)
            test_accs.append(test_accuracy)

        return train_losses, train_accs, test_losses, test_accs


# DO NOT MODIFY THIS FUNCTION
def load_data():
    # Load the data files
    print("Loading data...")
    x_train = np.load("x_train_cifar10_reduced.npz")["x_train"]
    x_test = np.load("x_test_cifar10_reduced.npz")["x_test"]
    y_train = np.load("y_train_cifar10_reduced.npz")["y_train"]
    y_test = np.load("y_test_cifar10_reduced.npz")["y_test"]

    # normalize the data
    mean = x_train.mean(axis=0)
    std = x_train.std(axis=0)
    x_train = (x_train - mean) / std
    x_test = (x_test - mean) / std

    # add implicit bias in the feature
    x_train = np.concatenate([x_train, np.ones((x_train.shape[0], 1))], axis=1)
    x_test = np.concatenate([x_test, np.ones((x_test.shape[0], 1))], axis=1)

    return x_train, y_train, x_test, y_test


if __name__ == "__main__":

    x_train, y_train, x_test, y_test = load_data()

    # print("Fitting the model...")
    svm = SVM(eta=0.0001, C=2, niter=200, batch_size=5000, verbose=False)
    train_losses, train_accs, test_losses, test_accs = svm.fit(x_train, y_train, x_test, y_test)

    # to infer after training, do the following:
    # y_inferred = svm.infer(x_test)
    #
    # ## to compute the gradient or loss before training, do the following:
    # y_train_ova = svm.make_one_versus_all_labels(y_train, 8)  # one-versus-all labels
    # svm.w = np.zeros([3073, 8])
    # y_inferred = svm.infer(x_test)
    # grad = svm.compute_gradient(x_train, y_train_ova)
    # loss = svm.compute_loss(x_train, y_train_ova)


    # graph gen
    import matplotlib.pyplot as plt

    epochs = 200
    c_values = [1, 10, 30]
    nb_c = len(c_values)

    def make_files():
        train_losses = np.empty((nb_c, epochs))
        train_accs = np.empty((nb_c, epochs))
        test_losses = np.empty((nb_c, epochs))
        test_accs = np.empty((nb_c, epochs))

        for i, c in enumerate(c_values):

            svm = SVM(eta=0.0001, C=c, niter=epochs, batch_size=5000, verbose=False)
            train_losses[i], train_accs[i], test_losses[i], test_accs[i] = svm.fit(x_train, y_train, x_test, y_test)


        np.save('train_losses', train_losses)
        np.save('train_accs', train_accs)
        np.save('test_losses', test_losses)
        np.save('test_accs', test_accs)


    def plot_for_c(title, arrays, labels, y_label):

        plt.plot(arrays[0], label=labels[0])
        plt.plot(arrays[1], label=labels[1])
        plt.plot(arrays[2], label=labels[2])
        plt.legend()
        plt.title(title + ' comparison by c value')
        plt.xlabel('epochs')
        plt.ylabel(y_label)
        plt.show()



    # make_files()

    train_losses = np.load('train_losses.npy')
    train_accs = np.load('train_accs.npy')
    test_losses = np.load('test_losses.npy')
    test_accs = np.load('train_accs.npy')


    plot_for_c('Train Loss', train_losses, c_values, 'loss')
    plot_for_c('Train Accuracy', train_accs, c_values, 'accuracy')
    plot_for_c('Test Loss', test_losses, c_values, 'accuracy')
    plot_for_c('Test Accuracy', test_accs, c_values, 'loss')
